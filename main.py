import os
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from typing import List, Optional, TypedDict, Literal

# メッセージの型定義
class ChatCompletionMessageParam(TypedDict):
    role: Literal['system', 'user', 'assistant']
    content: str

# OpenAI API クライアントの作成
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")  # APIキーは環境変数から取得
)

# メッセージ履歴
history: List[ChatCompletionMessageParam] = []

# メッセージを履歴に追加
def add_message(role: Literal['system', 'user', 'assistant'], content: str):
    history.append({"role": role, "content": content})

# OpenAI APIと対話
def chat_with_openai(messages: List[ChatCompletionMessageParam]) -> Optional[str]:
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # 最新のモデル名に更新
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        response_message = response.choices[0].message
        response_content = response_message.content
        return response_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# メイン処理
def main():
    mode = Prompt.ask("Please select Mode", choices=["autogen", "chat"])
    console = Console()

    if mode == "autogen":
        talk_about = Prompt.ask("Set the agenda")
        # 初期メッセージを履歴に追加
        add_message("user", talk_about)
        is_user_turn = False  # 最初はアシスタントのターン

        while True:
            if is_user_turn:
                system_message: ChatCompletionMessageParam = {
                    "role": "system",
                    "content": "You are Questioner. Please ask a question about the agenda."
                }
                # 質問を生成
                messages = [system_message] + history
                response_content = chat_with_openai(messages)
                if response_content:
                    add_message("user", response_content)
                    console.print(Markdown(f"### AI User\n{response_content}"))
                else:
                    break
            else:
                system_message: ChatCompletionMessageParam = {
                    "role": "system",
                    "content": "You are Assiatant. Please ask a question related to the agenda."
                }
                # 回答を生成
                messages = [system_message] + history
                response_content = chat_with_openai(messages)
                if response_content:
                    add_message("assistant", response_content)
                    console.print(Markdown(f"### AI Assistant\n{response_content}"))
                else:
                    break

            is_continue = Prompt.ask("Do you want to continue?", choices=["y", "n"])
            if is_continue.lower() == "n":
                break
            elif is_continue.lower() == "y":
                is_user_turn = not is_user_turn

    else:
        while True:
            user_message = Prompt.ask("Please input message")
            add_message("user", user_message)
            response_content = chat_with_openai(history)
            if response_content:
                add_message("assistant", response_content)
                console.print(Markdown(f"### AI Assistant\n{response_content}"))
            else:
                break

            is_continue = Prompt.ask("Do you want to continue?", choices=["y", "n"])
            if is_continue.lower() == "n":
                break

if __name__ == "__main__":
    main()
