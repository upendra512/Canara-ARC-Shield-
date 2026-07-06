import { promises as fs } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { config } from "../config/index.js";
import type { Circular } from "../types/domain.js";
import { sha256, randomId } from "../utils/crypto.js";
import { extractRefs } from "../utils/refExtractor.js";
import { deriveTitle } from "../utils/title.js";
import { fail } from "../utils/errors.js";
import { ensureDir } from "../store/persistence.js";
import { stateStore } from "../store/stateStore.js";
import { ledgerService } from "./ledgerService.js";

// pdf-parse ships as CommonJS with a debug-mode side effect on its index;
// require the implementation module directly to avoid it.
const require = createRequire(import.meta.url);
const pdfParse = require("pdf-parse/lib/pdf-parse.js") as (
  buf: Buffer,
) => Promise<{ text: string; numpages: number }>;

// pdf-parse's bundled pdf.js intermittently throws "bad XRef entry" on valid
// PDFs (~10% of the time). Retrying makes a single parse reliable.
async function parsePdf(buf: Buffer): Promise<{ text: string; numpages: number }> {
  let lastErr: unknown;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      return await pdfParse(buf);
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr;
}

export interface IntakeFile {
  originalName: string;
  mimeType: string;
  buffer: Buffer;
}

/** Authoritative check: PDFs begin with the %PDF- signature regardless of the
 *  client-declared content type (which is spoofable and often octet-stream). */
function isPdf(buffer: Buffer): boolean {
  return buffer.subarray(0, 5).toString("latin1") === "%PDF-";
}

/**
 * Layer 0 intake. The backend's job is mechanical: validate the file, extract
 * raw text + neutral file metadata, store the document, and record receipt on
 * the chain. It does NOT classify — regulator, sections, issued date and the
 * real title are decided by the Node 1 intelligence agent and filled in later.
 */
export const intakeService = {
  async ingest(file: IntakeFile): Promise<Circular> {
    let text = "";
    let pages = 1;
    const isPdfFile = isPdf(file.buffer);

    if (isPdfFile) {
      const parsed = await parsePdf(file.buffer).catch(() => {
        throw fail("UNPROCESSABLE", "Unable to parse PDF");
      });
      text = parsed.text ?? "";
      pages = parsed.numpages;
    } else {
      // Treat as plain text / markdown file
      text = file.buffer.toString("utf8");
      pages = Math.ceil(text.split("\n").length / 45) || 1;
    }

    if (text.trim().length === 0) {
      throw fail("UNPROCESSABLE", "Document contained no extractable text");
    }

    const documentHash = sha256(file.buffer);
    const id = randomId("CIR");
    const { refNumber, references } = extractRefs(text);
    
    // Save stored file path (using .pdf for PDF and .md/.txt for others)
    const isMd = file.originalName.endsWith(".md");
    const ext = isPdfFile ? ".pdf" : (isMd ? ".md" : ".txt");
    const storedPath = path.join(config.paths.documents, `${id}${ext}`);
    
    await ensureDir(config.paths.documents);
    await fs.writeFile(storedPath, file.buffer);
    
    // Write normalized text file
    const textPath = path.join(config.paths.documents, `${id}.txt`);
    await fs.writeFile(textPath, text, "utf8");

    const circular: Circular = {
      id,
      title: deriveTitle(null, file.originalName, refNumber),
      regulator: null,
      sections: [],
      issuedDate: null,
      receivedAt: new Date().toISOString(),
      stage: "RECEIVED",
      document: {
        filename: file.originalName,
        mimeType: file.mimeType,
        bytes: file.buffer.length,
        pages,
        sha256: documentHash,
        storedPath,
      },
      textLength: text.length,
      refNumber,
      references,
    };

    await stateStore.createCircular(circular);
    await ledgerService.recordCircularReceived(id, documentHash);
    return circular;
  },

  async extractText(circularId: string): Promise<string> {
    const circular = await stateStore.getCircular(circularId);
    if (!circular) throw fail("NOT_FOUND", `Unknown circular ${circularId}`);
    const textPath = path.join(path.dirname(circular.document.storedPath), `${circularId}.txt`);
    return fs.readFile(textPath, "utf8");
  },

  /**
   * Removes a circular: its state + pipeline and the stored PDF/text documents.
   * The append-only audit ledger is preserved (chain of custody is permanent).
   * Throws NOT_FOUND if the circular does not exist.
   */
  async remove(circularId: string): Promise<void> {
    const circular = await stateStore.getCircular(circularId);
    if (!circular) throw fail("NOT_FOUND", `Unknown circular ${circularId}`);
    const pdfPath = circular.document.storedPath;
    const textPath = pdfPath.replace(/\.pdf$/i, ".txt");
    await fs.rm(pdfPath, { force: true });
    await fs.rm(textPath, { force: true });
    await stateStore.deleteCircular(circularId);
  },
};
