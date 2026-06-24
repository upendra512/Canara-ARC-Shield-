"""
Offline smoke test for Node 1. No server, no internet, no LLM required.

Runs sample circular texts through the taxonomy classifier + clause extractor
and prints the IntelligenceResult-shaped verdict, asserting the contract Node 2
consumes (every clause has a section/title/text and obligation clauses survive).

Run:  python -m node1_intelligence.test_scenarios
"""

from node1_intelligence.classifier import detect_regulator
from node1_intelligence.extractor import analyze_text

SAMPLES = {
    "KYC periodic review (RBI)": (
        "Reserve Bank of India\n"
        "Subject: Periodic Updation of KYC\n"
        "Dated 15 June 2024\n"
        "1. Customer identity must be verified before account opening using PAN and Aadhaar.\n"
        "2. KYC records shall be retained for a period of 10 years.\n"
        "3. High-risk customers require enhanced due diligence (EDD).\n"
        "4. Customer KYC shall be updated every 2 years.\n"
    ),
    "Cyber MFA (RBI)": (
        "Subject: Cybersecurity Standards - Enhanced Controls\n"
        "All financial institutions must implement multi-factor authentication (MFA) "
        "with biometric verification for all customer-facing portals. "
        "Passwords must be changed every 90 days. "
        "All cyber incidents must be reported to the regulator within 6 hours of discovery.\n"
    ),
    "Capital adequacy (RBI)": (
        "Banks must maintain a minimum capital of 5,000,000 INR to ensure adequate "
        "capitalization. The capital adequacy ratio shall not fall below 11.5%.\n"
    ),
    "Data privacy consent": (
        "Customer consent must be obtained before data sharing with any third party. "
        "Personal data shall be deleted upon a valid request from the data subject.\n"
    ),
    "Paraphrase (no taxonomy keywords)": (
        "Subject: Account Onboarding Controls\n"
        "1. Before opening any account, the bank shall confirm the applicant truly is "
        "who they claim to be.\n"
        "2. Login screens shall demand a second proof of identity beyond the password.\n"
    ),
}


def main() -> None:
    failures = 0
    for name, text in SAMPLES.items():
        verdict = analyze_text(text, f"{name}.pdf", [])
        print("\n" + "=" * 70)
        print(name)
        print("=" * 70)
        print(f"regulator : {verdict['regulator']}")
        print(f"title     : {verdict['title']}")
        print(f"issuedDate: {verdict['issuedDate']}")
        print(f"sections  : {verdict['sections']}")
        for c in verdict["clauses"]:
            print(f"  [{c['section']:<8}] {c.get('_ruleType') or '-':<22} "
                  f"({c.get('_source', '-'):<8}) {c['text'][:55]}")
        try:
            assert verdict["regulator"] in {"RBI", "SEBI", "IRDAI", "MCA"}
            assert verdict["clauses"], "expected at least one clause"
            for c in verdict["clauses"]:
                assert c["section"] and c["title"] and c["text"]
        except AssertionError as exc:
            failures += 1
            print(f"  ✗ ASSERTION FAILED: {exc}")

    assert detect_regulator("issued by SEBI under LODR") == "SEBI"
    print("\n" + "=" * 70)
    print(f"Done. {len(SAMPLES)} scenarios, {failures} failure(s).")
    print("=" * 70)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
