import os
from vertexai.preview.generative_models import GenerativeModel, Tool
from vertexai.preview import rag
import vertexai

class ReconciliationAgent:
    def __init__(self, project_id, location=None):
        self.project_id = project_id
        self.location = location or os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
        vertexai.init(project=self.project_id, location=self.location)
        
        self.rag_corpus_name = self._load_corpus_name()
        self.rag_retrieval_tool = self._create_retrieval_tool()
        self.rag_gemini_model = self._create_gemini_model()

    def _load_corpus_name(self):
        with open("rag_corpus_names.txt", "r") as f:
            for line in f:
                if line.startswith("Reconciliation Corpus:"):
                    return line.split(":")[1].strip()
        raise ValueError("Reconciliation Corpus name not found in rag_corpus_names.txt")

    def _create_retrieval_tool(self):
        return Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_corpora=[self.rag_corpus_name],
                    similarity_top_k=5,
                    vector_distance_threshold=0.7,
                ),
            )
        )

    def _create_gemini_model(self):
        return GenerativeModel(
            "gemini-1.5-flash-002",
            tools=[self.rag_retrieval_tool],
            system_instruction=["""
# RAG Reconciliation Agent System Instruction

您是一個專門處理男女關係爭執的和解代理。您的任務是接收法官對男女爭執事件的總結,搜尋RAG資料庫以找到適當的應對策略,並為雙方提供照顧對方心情的和解方式。

## 輸入
- 法官對男女爭執事件的總結

## 處理步驟
1. 分析總結,確定雙方最在意的爭執點。
2. 在RAG資料庫中搜尋相關的應對策略。
3. 結合爭執點和策略,為男方和女方分別制定和解方案。

## 輸出格式
請按以下格式提供和解建議:

```
男女爭執重點：
[簡要描述雙方最在意的爭執點]

應對策略：
[列出從RAG資料庫中找到的相關策略]

給男方的和解建議：
[基於爭執點和策略,提供照顧女方心情的和解方式]

給女方的和解建議：
[基於爭執點和策略,提供照顧男方心情的和解方式]
```

注意：請確保和解建議具體、實用,並充分考慮雙方段男女方對話紀錄和的感受。避免使用籠統或模糊的表述。
"""]
        )

    def get_reconciliation_advice(self, context):
        prompt = f"Based on the following context, provide specific reconciliation advice: {context}"
        response = self.rag_gemini_model.generate_content(prompt)
        return response.text

    def analyze_conflict(self, conflict_description):
        prompt = f"Analyze the following conflict and provide insights: {conflict_description}"
        response = self.rag_gemini_model.generate_content(prompt)
        return response.text

    def suggest_mediation_techniques(self, situation):
        prompt = f"Suggest appropriate mediation techniques for the following situation: {situation}"
        response = self.rag_gemini_model.generate_content(prompt)
        return response.text

    def evaluate_resolution_progress(self, initial_state, current_state):
        prompt = f"Compare the initial state of the conflict: '{initial_state}' with the current state: '{current_state}'. Evaluate the progress of resolution."
        response = self.rag_gemini_model.generate_content(prompt)
        return response.text

def test_reconciliation_agent():
    project_id = "semiotic-effort-439102-k9"  # 请替换为你的实际项目ID
    agent = ReconciliationAgent(project_id=project_id)

    print("Testing ReconciliationAgent...")

    # 测试 get_reconciliation_advice
    context = "一對情侶在爭吵後進入了冷戰階段，女方選擇沉默不語，男方不知如何打破僵局。"
    print("\n1. Testing get_reconciliation_advice:")
    advice = agent.get_reconciliation_advice(context)
    print(f"Context: {context}")
    print(f"Advice: {advice}\n")

    # 测试 analyze_conflict
    conflict = "在爭吵過程中，一方不小心說出了涉及對方家人的侮辱性言語，導致爭吵升級。"
    print("2. Testing analyze_conflict:")
    analysis = agent.analyze_conflict(conflict)
    print(f"Conflict: {conflict}")
    print(f"Analysis: {analysis}\n")

    # 测试 suggest_mediation_techniques
    situation = "一對情侶經常因為小事爭吵，但都不善於表達自己的真實感受，導致問題無法得到有效解決。"
    print("3. Testing suggest_mediation_techniques:")
    techniques = agent.suggest_mediation_techniques(situation)
    print(f"Situation: {situation}")
    print(f"Suggested techniques: {techniques}\n")

    # 测试 evaluate_resolution_progress
    initial_state = "情侶間經常因為瑣事爭吵，且習慣用冷戰來對抗。"
    current_state = "雙方開始嘗試在爭吵時控制情緒，避免說出傷害對方的話，並努力在當天解決問題。"
    print("4. Testing evaluate_resolution_progress:")
    evaluation = agent.evaluate_resolution_progress(initial_state, current_state)
    print(f"Initial state: {initial_state}")
    print(f"Current state: {current_state}")
    print(f"Evaluation: {evaluation}\n")

    print("Testing complete.")

if __name__ == "__main__":
    test_reconciliation_agent()