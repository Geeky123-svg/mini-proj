import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn import functional as F
import time
import os

# -----------------------------
# CONFIG
# -----------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
INPUT_CSV = "NIFTY50_news_impact_binary.csv"
OUTPUT_CSV = "NIFTY50_sentiment_results.csv"
BATCH_SIZE = 32  

# -----------------------------
# LOAD FINBERT
# -----------------------------
print(f"Loading FinBERT on {DEVICE}...")
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(DEVICE)
model.eval()

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------
def detect_sentiment(texts):
    """Predicts sentiment for a list of strings using FinBERT."""
    if not texts:
        return []
        
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(DEVICE)
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
    
    labels = ["positive", "negative", "neutral"]
    results = []
    
    for i in range(len(texts)):
        idx = probs[i].argmax().item()
        # Score: Positive prob - Negative prob
        score = (probs[i][0] - probs[i][1]).item()
        results.append((labels[idx], round(score, 4)))
    return results

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        exit()

    df_full = pd.read_csv(INPUT_CSV)
    total_rows = len(df_full)

    # --- RESUME LOGIC ---
    if os.path.exists(OUTPUT_CSV):
        try:
            df_existing = pd.read_csv(OUTPUT_CSV)
            start_idx = len(df_existing)
            print(f"Resuming from row {start_idx}...")
        except pd.errors.EmptyDataError:
            start_idx = 0
    else:
        start_idx = 0
        # Create empty file with headers
        pd.DataFrame(columns=df_full.columns.tolist() + ["sentiment_label", "sentiment_score"]).to_csv(OUTPUT_CSV, index=False)

    # --- BATCH PROCESSING ---
    start_time = time.time()

    for i in range(start_idx, total_rows, BATCH_SIZE):
        batch_df = df_full.iloc[i : i + BATCH_SIZE].copy()
        
        # Filter: Only send rows to the GPU where Impact == 1
        impact_mask = batch_df["Impact (1/0)"] == 1
        impact_rows = batch_df[impact_mask]
        
        # Initialize default values for the whole batch
        batch_df["sentiment_label"] = "skipped/neutral"
        batch_df["sentiment_score"] = 0.0

        if not impact_rows.empty:
            # Inference only on high-impact news
            titles = impact_rows["title"].tolist()
            predictions = detect_sentiment(titles)
            
            # Map predictions back to the correct rows
            labels = [p[0] for p in predictions]
            scores = [p[1] for p in predictions]
            
            batch_df.loc[impact_mask, "sentiment_label"] = labels
            batch_df.loc[impact_mask, "sentiment_score"] = scores

        # Append to CSV immediately (to save progress)
        batch_df.to_csv(OUTPUT_CSV, mode='a', index=False, header=False)
        
        elapsed = time.time() - start_time
        print(f"[{elapsed:.1f}s] Processed {min(i + BATCH_SIZE, total_rows)}/{total_rows} rows...")

    print(f"\n--- Finished! ---\nResults saved to: {OUTPUT_CSV}")