import json
import os
from fastapi.testclient import TestClient
from main import app

def run_evaluation():
    client = TestClient(app)
    
    # 1. Upload rag_qa.pdf
    pdf_path = "rag_qa.pdf"
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Target PDF file '{pdf_path}' not found in workspace.")
        
    with open(pdf_path, "rb") as f:
        upload_resp = client.post("/documents/upload", files={"file": ("rag_qa.pdf", f, "application/pdf")})
    
    print("Upload response:", upload_resp.json())
    assert upload_resp.status_code in (200, 201)
    doc_id = upload_resp.json()["document"]["document_id"]
    
    eval_questions = [
        # --- Positive Test Cases (In-Corpus from rag_qa.pdf) ---
        {
            "id": 1,
            "category": "Direct Lookup",
            "question": "When was Suresh Tech founded and where is its headquarters?",
            "expected_contains": ["2016", "Kathmandu"],
            "should_refuse": False
        },
        {
            "id": 2,
            "category": "Direct Lookup",
            "question": "How many paid annual leave days do employees receive under the 2025 policy?",
            "expected_contains": ["21 days"],
            "should_refuse": False
        },
        {
            "id": 3,
            "category": "Cross-Region Policy",
            "question": "How many paid sick days are allotted for employees in Nepal vs Bengaluru?",
            "expected_contains": ["12", "10"],
            "should_refuse": False
        },
        {
            "id": 4,
            "category": "Product Pricing",
            "question": "What are the pricing tiers and cost for SureshDesk under the 2025 pricing sheet?",
            "expected_contains": ["Free", "Pro", "10"],
            "should_refuse": False
        },
        {
            "id": 5,
            "category": "Security Protocol",
            "question": "What should an employee do if a company-issued device is lost or stolen?",
            "expected_contains": ["helpdesk@Sureshtech.example", "2 hours"],
            "should_refuse": False
        },
        
        # --- Negative Test Category 1: Plausible Fake Features ---
        {
            "id": 6,
            "category": "Negative - Plausible Fake Feature",
            "question": "How much does the SureshDesk Ultra plan cost per user?",
            "expected_contains": ["couldn't find"],
            "should_refuse": True
        },
        
        # --- Negative Test Category 2: Standard HR Policies (Omitted) ---
        {
            "id": 7,
            "category": "Negative - Omitted HR Policy",
            "question": "What is Suresh Tech's 401(k) or Provident Fund matching percentage policy?",
            "expected_contains": ["couldn't find"],
            "should_refuse": True
        },
        {
            "id": 8,
            "category": "Negative - Omitted HR Policy",
            "question": "How many days of paid pet bereavement leave does Suresh Tech allow?",
            "expected_contains": ["couldn't find"],
            "should_refuse": True
        },
        
        # --- Negative Test Category 3: Fake Technical Features ---
        {
            "id": 9,
            "category": "Negative - Fake Tech Feature",
            "question": "How do I configure offline peer-to-peer sync on the SureshDesk desktop client?",
            "expected_contains": ["couldn't find"],
            "should_refuse": True
        },
        
        # --- Negative Test Category 4: Fabricated Historical Events ---
        {
            "id": 10,
            "category": "Negative - Fabricated History",
            "question": "What were the office working hours for Suresh Tech's London branch in 2022?",
            "expected_contains": ["couldn't find"],
            "should_refuse": True
        },
        
        # --- Tool Call Test Cases ---
        {
            "id": 11,
            "category": "Tool Call - Issue Ticket",
            "question": "My laptop screen is broken, please create a support ticket for me.",
            "expected_contains": ["ticket", "created"],
            "expect_tool": "create_issue_tickets",
            "should_refuse": False
        },
        {
            "id": 12,
            "category": "Tool Call - Bug Report",
            "question": "Please log a bug ticket for login error on staging environment.",
            "expected_contains": ["bug", "ticket"],
            "expect_tool": "create_issue_tickets",
            "should_refuse": False
        },
        {
            "id": 13,
            "category": "Out-of-Domain Refusal",
            "question": "Who won the 2022 FIFA World Cup in Qatar?",
            "expected_contains": ["couldn't find"],
            "should_refuse": True
        }
    ]

    eval_results = []
    
    for item in eval_questions:
        chat_resp = client.post("/chat", json={"question": item["question"]})
        res_data = chat_resp.json()
        
        answer = res_data.get("answer", "")
        sources = res_data.get("sources", [])
        tool_calls = res_data.get("tool_calls", [])
        
        passed = True
        notes = "Passed evaluation criterion."
        
        if item["should_refuse"]:
            if "couldn't find" not in answer.lower():
                passed = False
                notes = "Failed: Model hallucinated answer instead of refusing."
        else:
            if "expect_tool" in item:
                tool_names = [tc.get("function_name") for tc in tool_calls]
                if item["expect_tool"] not in tool_names:
                    passed = False
                    notes = f"Failed: Expected tool call {item['expect_tool']}."
            else:
                for keyword in item.get("expected_contains", []):
                    if keyword.lower() not in answer.lower():
                        passed = False
                        notes = f"Failed: Missing expected keyword '{keyword}' in generated answer."
                        break
                    
        eval_results.append({
            "test_id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "generated_answer": answer,
            "retrieved_sources": sources,
            "executed_tool_calls": tool_calls,
            "passed": passed,
            "quality_notes": notes
        })

    # --- Metric Calculations ---
    total_tests = len(eval_results)
    total_passed = sum(1 for r in eval_results if r["passed"])
    
    refusal_tests = [item for item in eval_questions if item["should_refuse"]]
    refusal_ids = {item["id"] for item in refusal_tests}
    refusal_passed = sum(1 for r in eval_results if r["test_id"] in refusal_ids and r["passed"])
    
    refusal_accuracy = (refusal_passed / len(refusal_tests) * 100) if refusal_tests else 100.0
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests else 100.0

    summary = {
        "target_pdf": pdf_path,
        "total_tests": total_tests,
        "total_passed": total_passed,
        "overall_pass_rate_percent": round(overall_pass_rate, 2),
        "total_refusal_tests": len(refusal_tests),
        "refusal_passed": refusal_passed,
        "refusal_accuracy_percent": round(refusal_accuracy, 2),
        "results": eval_results
    }
        
    with open("eval_results.json", "w") as f:
        json.dump(summary, f, indent=2)
        
    print(f"\n==========================================")
    print(f"EVALUATION COMPLETE ({pdf_path})")
    print(f"==========================================")
    print(f"Total Tests Run   : {total_tests}")
    print(f"Overall Pass Rate  : {total_passed}/{total_tests} ({overall_pass_rate:.1f}%)")
    print(f"Refusal Accuracy   : {refusal_passed}/{len(refusal_tests)} ({refusal_accuracy:.1f}%)")
    print(f"Saved results to eval_results.json")
    print(f"==========================================\n")

if __name__ == "__main__":
    run_evaluation()
