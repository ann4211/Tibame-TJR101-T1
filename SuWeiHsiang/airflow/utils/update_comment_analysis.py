from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import time
import os
from pathlib import Path

load_dotenv()
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)

def access_openai(input_prompt, deal_range):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "你是一位專業的評論分析師，專門用於判斷餐廳評論是否疑似為水軍留言。"
                                            "對每則評論資訊請根據以下規則進行判斷：\n\n"
                                            "1. 回答 T（是水軍）或 F（非水軍）。\n"
                                            "2. 如果是 T，請用 10 字以內說明原因。\n"
                                            "3. 無論 T 或 F，請以 1~5 的整數評估水軍可能性分數，5 分表示最有可能。\n\n"
                                            "請依照以下格式回答：\n"
                                            "編號) T 或 F // 分數（1~5） // 原因（若為 F 則不用寫）\n\n"
                                            "範例：\n"
                                            "1) T // 5 // 重複字句太多\n"
                                            "2) F // 1 // \n"
                                            "接下來是任務說明與資料："},
                {"role": "user", "content": input_prompt}
            ],
            temperature=0.5
        )
        if not response or not response.choices:
            print(f"處理第 {deal_range} 筆，回傳內容有誤")
            return "無法取得回覆"
    
        usage = response.usage
        print(f"[Token 使用狀況] input: {usage.prompt_tokens}｜output: {usage.completion_tokens}｜total: {usage.total_tokens}")

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"處理第 {deal_range} 筆時發生錯誤：{e}")
        time.sleep(20)
        return "無法取得回覆"
    
def fake_examples_csv(df_fake_sample, amount):
    examples = ["以下是已知的水軍評論範例：\n"]
    amount = min(amount, len(df_fake_sample))
    df_fake_sample = df_fake_sample.sample(n=amount, random_state=None)
    for i, row in enumerate(df_fake_sample.iterrows(), start=1):
        name = row[1]["客戶類別"]
        media = row[1]["發佈社群平台"]
        who = row[1]["留言者身份"]
        comment = row[1]["留言內容"]

        example = f'''(範例{i})
        客戶類別或名稱：{name}
        留言平台：{media}
        留言者身份：{who}
        內容：{comment}
        '''
        examples.append(example)
    
    examples.append("\n請根據上述範例與經驗判斷，以下留言是否疑似為水軍評論。"
                    "若留言內容為空，請依留言者身份與留言時間判斷其是否有效，並給予水軍可能性評分（1~5 分）。\n"
                    "水軍可能性評分（1~5 分）標準：\n"
                    "1 分：極低可能，留言自然、有細節、語氣真實，無任何異常\n"
                    "2 分：低可能，留言簡短但可信，或無內容但其他資訊合理\n"
                    "3 分：中等可能，有部分異常（如太簡略、過於正面），但無法確定\n" 
                    "4 分：高可能，明顯出現水軍特徵，如重複語句、無細節、語氣誇張\n"
                    "5 分：極高可能，具備多項水軍特徵，或明顯機器生成、不合理內容\n"
                    "請勿因評論內容過短或無內容就直接給予 4 或 5 分，應綜合身份、時間、語氣等多項資訊判斷。\n"
                    
                    "另外，除了參考範例外，也請特別留意常見水軍評論特徵，若評論中包含以下內容，請提高懷疑程度並綜合評分：\n"
                    "- 不自然地提及價格、優惠、折扣，如：只要199就吃到飽、價格超佛\n"
                    "- 過度行銷語氣，如：一定要試試、超超推、網美打卡聖地\n"
                    "- 提及網紅、部落客、YouTuber 推薦等，如：某某推薦來的\n"
                    "- 使用重複性很高的描述，如：好吃好吃好吃、超級好吃超級推薦\n"
                    "- 沒有實際內容，只留下評價星數、emoji 或無意義文字（如：推！👍）\n"
                    "若評論中出現以上特徵之一，可視為潛在水軍跡象，請提高警覺；若出現多項，應考慮評為 T 並給予 4 分或 5 分。\n")
                    # "注意：下列留言無內容或是內容較短時，請依據留言者身份與評價時間進行推估，但不可單純因為無內容或內容較短就判定為水軍。\n")
                    # "請注意：並非所有沒有留言內容或是內容較短的評價都是水軍。\n"
                    # "若遇到無留言內容或是內容較短的情況，請結合以下資訊綜合評估：\n"
                    # "- 留言者身份是否異常（如匿名或格式異常）\n"
                    # "- 留言時間是否集中（如短時間大量評價）\n"
                    # "- 評價星等是否不自然（如全為五星）\n"
                    # "如果無法明確判斷為水軍，請給予中間分數（如 2 或 3），並標註為 F。\n")

    #print(examples)
    return "\n".join(examples)

def prompt_text(df_group, deal_range , df_fake_sample , amount):
    fake_prompts = fake_examples_csv(df_fake_sample, amount)

    prompts = []
    for idx, (i, row) in enumerate(df_group.iterrows(), start=1):
        name = row["st_name"]
        star = row["rating_star"]
        comment = row["content_clean"]
        who = row["local_guide"]
        wh_time = row["months_ago"]

        info = f'''
            留言者評論資訊
            店名：{name}
            留言者身份：{who}
            留言時間：{wh_time}個月前
            評價星等：{star}
            評論內容：{comment}

            以上，總計 {len(df_group)} 筆留言，請逐一依規則判斷，並依照指定格式回覆：
        '''
        prompts.append(f"({idx})" + info)


    print(f"正在處理第 {deal_range} 則留言")
    return fake_prompts + "\n".join(prompts) + "\n"

def output_csv(df, df_group, output_text):
    lines = output_text.strip().split("\n")
    if len(lines) != len(df_group):
        print(f"回傳筆數與預期不一致：預期 {len(df_group)}，實際 {len(lines)}\n內容如下：\n{output_text}")
        return

    for idx, line in enumerate(lines):
        try:
            if "//" not in line or ")" not in line:
                print(f"格式錯誤：{line}")
                continue
                
            id_part, result_part = line.split(")", 1)
            fake_comment, fake_level, fake_reason = result_part.split("//", 2)

            df_index = df_group.index[idx]
            df.at[df_index, "fake_comment"] = fake_comment.strip()
            df.at[df_index, "fake_level"] = int(fake_level.strip())
            df.at[df_index, "fake_reason"] = fake_reason.strip()

        except Exception as e:
            print(f"判別錯誤：{line}｜錯誤訊息：{e}")
            df_index = df_group.index[idx]
            df.at[df_index, "fake_comment"] = "無法判斷"
            df.at[df_index, "fake_level"] = "無法判斷"
            df.at[df_index, "fake_reason"] = "無法判斷"

    path = Path(f"./data/comment_analysis_result.csv")
    if path.exists():
        df_group.to_csv(path, index=False, header=False, encoding='utf-8-sig', mode="a") 
    else:
        df_group.to_csv(path, index=False, header=True, encoding='utf-8-sig', mode="a")

    print("已完成輸出")

def main():
    df = pd.read_csv("./data/comment_analysis.csv")
    df_fake = pd.read_csv("./data/fake_comments.csv")
    df_output = pd.read_csv("./data/comment_analysis_result.csv")
    df_output = df_output[0:0]
    df_output.to_csv("./data/comment_analysis_result.csv",index=False,header=True,encoding="utf-8-sig")

    df["fake_comment"] = ""
    df["fake_level"] = ""
    df["fake_reason"] = ""
    group_quiz = 200

    for start in range(0 , len(df) , group_quiz):
        df_group = df.iloc[start:start + group_quiz]
        deal_range = f"{start + 1} ~ {start + group_quiz}"

        df_fake_sample = df_fake.copy()
        amount = 5

        input_prompt = prompt_text(df_group, deal_range , df_fake_sample , amount)
        output_text = access_openai(input_prompt, deal_range)
        if output_text == "無法取得回覆":
            continue
        output_csv(df, df_group, output_text)

        time.sleep(60)
