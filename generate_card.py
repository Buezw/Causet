import requests
import json
import re
from os import getenv

# DeepSeek API key 建议用环境变量管理
API_KEY = "sk-1a1cee14af3543459ca5656c509a6a0e"
API_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_card(topic: str, model="deepseek-chat") -> str:
    """
    根据主题生成知识卡片 Markdown 内容
    """
    prompt = f"""
你是一个理工类知识卡片生成助手，请根据用户给出的主题“{topic}”生成一条结构化的知识卡片，格式为 Markdown（适配 md2card.com）。请严格使用如下字段，内容尽量专业、简洁，输出结构规范，返回内容必须包裹在一对 ```markdown 代码块中。

- title：固定为该知识点的名称，即“{topic}”
- body：用专业、准确的语言解释该知识点的核心定义、原理、结构组成，指出其适用范围和学术意义，避免口语化，控制在 100 字以内。
- latex：用 LaTeX 表达的核心公式（如有）
- example：结合真实应用场景（如科研、工程、现实世界）举例说明该知识点在实际中的体现或用途，简洁清晰，2~3 句内
- quiz：一个相关的交互题，格式如下：
  - type："判断题" 或 "选择题"
  - question：题干
  - options：备选项（判断题为["是", "不是"]；选择题至少 3 个选项，确保涵盖常见错误项，所有选项前加上"A. B. C. D." 等字母编号）
  - answer：正确答案内容（文本，需与 options 中某一项完全一致）
  - explanation：一句解释（说明正确答案的理由，尽量具体）
- misconception：指出一个与该知识点相关的常见误解，并简要说明其错误之处与正确理解方式
- image_prompt：请基于该知识点，为生成一张教学插图设计一个英文提示词（prompt），用于图像生成模型（如 GPT-4o 或 DALL·E）。描述应包含画面场景、关键元素、相对关系和风格要求。图像必须不含文字，不要出现任何公式、标签或说明性文字。风格应简洁、线稿或卡片风格，适合作为教学辅助配图。

Markdown 格式如下所示，请严格遵循并直接输出：

```markdown
# {{title}}

---

**定义说明：**  
{{body}}

---

**数学表达：**
$$ {{latex}} $$

---

**现实例子：**  
{{example}}

---

**常见误区：**  
🚫 **误区：** {{错误说法}}  
✅ **澄清：** {{解释说明}}

---

**随堂测验：**  
Q：{{question}}

{{选项列表，每行以 - A./B./C. 开头}}

✅ **正确答案：** {{answer}}  
🧠 **解析：** {{explanation}}

---

**图像生成提示：**  
🎨 {{image_prompt}}
```
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个严谨、专业的知识内容生成器。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return content.strip()
        else:
            print(f"❌ DeepSeek API 请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)
            return ""

    except Exception as e:
        print("生成失败：", e)
        return ""
import os

def save_markdown(md: str, topic: str):
    if not md:
        print("⚠️ 没有生成内容，跳过保存。")
        return

    # 去掉开头和结尾的 ```markdown 和 ```
    cleaned = re.sub(r"^```markdown\s*", "", md.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())

    # 将 ```math ... ``` 块替换为单行 $$...$$
    def replace_math_block(match):
        formula = match.group(1).strip().replace("\n", " ")
        return f"$$ {formula} $$"

    cleaned = re.sub(r"```math\s*(.*?)\s*```", replace_math_block, cleaned, flags=re.DOTALL)

    # 保存文件
    os.makedirs("cards", exist_ok=True)
    filename = f"cards/{topic}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"✅ 已保存至：{filename}")
# 示例调用（开发测试）
if __name__ == "__main__":
    md = generate_card("牛顿第二定律")
    print(md)
    save_markdown(md, "牛顿第二定律")