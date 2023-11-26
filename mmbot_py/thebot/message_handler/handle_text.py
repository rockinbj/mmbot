from thebot import commander
from thebot.my_bot import MyBot
from thebot.types import MM_ADDR_TYPES, MessageHandlerContext


def handler(bot: MyBot, ctx: MessageHandlerContext):
    logger = bot.logger

    msg_text = ctx.msgview.data_parsed

    # ----- 过滤消息
    #   过滤未知的用户类型
    if not ctx.msguser.user_type:
        logger.warn(f"Ignore unsupported user's message: {ctx.msgview.to_dict()}")
        return
    #   过滤来自机器人的消息。 不然机器人直接可能相互收发消息无止境
    if ctx.msguser.user_type == MM_ADDR_TYPES.MIXIN_APP:
        logger.info("Ignore mixin app user's message")
        return
    #   过滤群组中的部分消息
    if ctx.msguser.is_in_group:
        # 忽略没有@本机器人的消息（避免群组内多个机器人之间互回消息，因为机器人的发的消息，没有@，别的机器人也能收到）
        sign_str = f"@{bot.profile.mixin_number} "
        if sign_str not in msg_text:
            logger.info(f"Ignore text message in group, that not @ the bot: {msg_text}")
            return

        # # filter out group messages not from admins and owner
        # bot.get_mixin_group_profile(ctx.msguser, ctx.msgview.conversation_id)
        # if ctx.msgview.user_id not in ctx.msguser.group_admin_user_id_list:
        #     logger.debug(f"Ignore group message:{ctx.msgview.message_id} not from admins")
        #     return

    # commander.handle(bot, ctx, msg_text)
    commander.handle_new(bot, ctx, msg_text)
