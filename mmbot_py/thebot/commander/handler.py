from pathlib import Path

from openai import OpenAI
from thebot.my_bot import MyBot
from thebot.types import MessageHandlerContext


def handle(
    bot: MyBot,
    ctx: MessageHandlerContext,
    msg_text: str,
):
    cmd = msg_text.lower()
    if cmd in ["hi", "hello"]:
        bot.add_replying_text_message(ctx, "Welcome!")
    elif cmd == "steve jobs":
        bot.add_replying_markdown_message(ctx, "**Stay hungry, stay foolish.**")
    else:
        bot.add_replying_text_message(ctx, "Unknown command", True)


def handle_new(bot: MyBot, ctx: MessageHandlerContext, msg_text: str,):
    cmd = msg_text.lower()
    openai_client = OpenAI(api_key='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')
    path_data = Path(__file__).resolve().parent.parent.parent.parent/'data'
    file_prompt = path_data/'prompt.txt'
    file_hist = path_data/'chat_history.txt'

    # 读取历史记录
    if file_hist.exists():
        history = file_hist.read_text(encoding='utf8')
    else:
        history = ""

    msg = []
    # 设置前导语
    msg.append({"role": "system", "content": file_prompt.read_text(encoding='utf8')})
    # 添加历史记录
    if history:
        for line in history.split('\n'):
            if line.startswith("User:"):
                msg.append({"role": "user", "content": line[5:]})
            elif line.startswith("Bot:"):
                msg.append({"role": "assistant", "content": line[4:]})
    # 添加当前消息
    msg.append({"role": "user", "content": cmd})

    chat_completion = openai_client.chat.completions.create(
        messages=msg,
        model="gpt-3.5-turbo",
        max_tokens=10000,
    )
    reply = chat_completion.choices[0].message.content

    # 保存历史记录
    file_hist.write_text(f'{history}\nUser: {cmd}\nBot: {reply}\n', encoding='utf8')

    # Send the ChatGPT reply back to the user
    bot.add_replying_text_message(ctx, reply)
