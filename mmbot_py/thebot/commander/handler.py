import time
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
    path_root = Path(__file__).resolve().parent.parent.parent.parent
    path_data = path_root/'data'
    file_prompt = path_data/'prompt.txt'
    file_hist = path_data/'chat_history.txt'
    file_openai_key = path_root/'config'/'openai_key'

    # 特殊指令
    match cmd:
        case '/???':
            bot.add_replying_markdown_message(ctx, (path_data/'help.txt').read_text())
            return
        case '7890909':
            file_hist.rename(path_data/f'chat_history.{int(time.time())}')
            print(f'reset chat_history.txt OK.')
            return

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

    openai_client = OpenAI(api_key=file_openai_key.read_text().strip())
    chat_completion = openai_client.chat.completions.create(
        messages=msg,
        model="gpt-3.5-turbo-16k",
        # max_tokens=10000,
    )
    reply = chat_completion.choices[0].message.content

    # 保存历史记录
    file_hist.write_text(f'{history}\nUser: {cmd}\nBot: {reply}\n', encoding='utf8')

    # Send the ChatGPT reply back to the user
    bot.add_replying_text_message(ctx, reply)
