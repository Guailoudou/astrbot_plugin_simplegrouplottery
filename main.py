from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import os,json,random,time,asyncio
@register("simplegrouplottery", "Guailoudou", "一个简单的 群抽奖 插件", "1.0.0")
class LotteryPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("参与抽奖")
    async def addqq(self, event: AstrMessageEvent):
        """参加""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        # message_str = event.message_str # 用户发的纯文本消息字符串
        message_obj = event.message_obj # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        
        qq = message_obj.sender.user_id
        #写入json文件，文件不存在则创建
        if not os.path.exists("code.json"):
            with open("code.json", "w") as f:
                json.dump({}, f)
        with open("code.json", "r") as f:
            code = json.load(f)
        if qq in code:
            yield event.plain_result("你已经申请过参与抽奖了，请勿重复参与")
            return
        else:
            code[qq] = user_name
            with open("code.json", "w") as f:
                json.dump(code, f)

        yield event.plain_result(f"用户{message_obj.sender.user_id}参与成功") # 发送一条纯文本消息

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("getqqs")
    async def getqqs(self, event: AstrMessageEvent):
        """获取QQ列表"""
        with open("code.json", "r") as f:
            code = json.load(f)
            chain = [
                Comp.Plain(f"{code}")
            ]
        yield event.chain_result(chain)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("rmqq")
    async def rmqq(self, event: AstrMessageEvent, qq: str):
        """删除QQ"""
        with open("code.json", "r") as f:
            code = json.load(f)
            if qq not in code and qq != "all":
                chain = [
                    Comp.Plain("QQ不存在")
                ]
                yield event.chain_result(chain)
                return
        if qq == "all":
            code.clear()

            chain = [
                Comp.Plain("已删除所有QQ")
            ]
            yield event.chain_result(chain)
        else:
            del code[qq]
            yield event.chain_result([Comp.Plain(f"删除 {qq} 成功")])
        with open("code.json", "w") as f:
            json.dump(code, f)
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("rmgroup")
    async def rmgroup(self, event: AstrMessageEvent):
        """删除all开奖源群"""
        with open("msggroup.json", "w") as f:
            json.dump([], f)
        yield event.chain_result([Comp.Plain("删除成功")])

    

    async def timeout(self, event: AstrMessageEvent,times: int):
        # async def timed_task(event: AstrMessageEvent,times: int):
        #     await asyncio.sleep(times)
        #     yield event.chain_result([Comp.Plain(f"已等待{times}秒")])
        try:
            await asyncio.sleep(times)
        except asyncio.CancelledError:
            chain = event.chain_result([Comp.Plain(f"已取消抽奖")])
            with open("msggroup.json", "r") as f:
                msgg = json.load(f)
            for i in msgg:
                await self.context.send_message(i,event.chain_result(chain))
            if event.unified_msg_origin not in msgg:
                await self.context.send_message(event.unified_msg_origin,event.chain_result(chain))
            return
        logger.info("已等待{}秒".format(times))
        await LotteryPlugin.Lotterystart(self, event)
        # yield event.chain_result([Comp.Plain(f"1开始等待{times}秒")])
        # await asyncio.sleep(times)
        # yield event.chain_result([Comp.Plain(f"已等待{times}秒")])
        # task = asyncio.create_task(timed_task(event,times))
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("开始抽奖")
    async def Lotterystart(self, event: AstrMessageEvent):
        logger.info("开始抽奖")
        # yield event.chain_result([Comp.Plain(f"将在{times}秒")])
        # await asyncio.sleep(times)
        with open("code.json", "r") as f:
            code = json.load(f)
        length = len(code)
        num = random.randint(0, length - 1)
        info = list(code.items())[num]
        chain = [
            Comp.At(qq=info[0]), 
            Comp.Face(id=144),
            Comp.Plain(f"恭喜你中奖了"),
            Comp.Face(id=144),
            Comp.Plain(f" \n中奖信息：\nQQ号：{info[0]}\n用户名：{info[1]}"),
            Comp.Image.fromURL("https://file.gldhn.top/img/1721313589276slitu2.png"),
        ]

        if not os.path.exists("winlist.json"):
            with open("winlist.json", "w") as f:
                json.dump([], f)
        with open("winlist.json", "r") as f:
            winlist = json.load(f)
        winlist.append({
            "time": time.time(),
            "info": info
        })
        with open("winlist.json", "w") as f:
            json.dump(msgg, f)

        with open("msggroup.json", "r") as f:
            msgg = json.load(f)
        for i in msgg:
            await self.context.send_message(i,event.chain_result(chain))
        if event.unified_msg_origin not in msgg:
            await self.context.send_message(event.unified_msg_origin,event.chain_result(chain))
        # yield event.chain_result(chain)


    task = None
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("定时抽奖")
    async def timestart(self, event: AstrMessageEvent,times: int):
        logger.info(times)
        # LotteryPlugin.Lotterystart(self, event)
        global task
        task = asyncio.create_task(LotteryPlugin.timeout(self, event,times))
        # yield event.plain_result(f"已开始定时抽奖，请等待{times}秒")
        chain = [
            Comp.Plain(f"已开始定时抽奖，将于{times}秒后开奖"),
        ]
        with open("msggroup.json", "r") as f:
            msgg = json.load(f)
        for i in msgg:
            await self.context.send_message(i,event.chain_result(chain))
        if event.unified_msg_origin not in msgg:
            await self.context.send_message(event.unified_msg_origin,event.chain_result(chain))
        # result = await task
        # yield result
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("setmsggroup")
    async def setmsggroup(self, event: AstrMessageEvent):
        if not os.path.exists("msggroup.json"):
            with open("msggroup.json", "w") as f:
                json.dump([], f)
        with open("msggroup.json", "r") as f:
            msgg = json.load(f)
        logger.info(msgg)
        msgg.append(event.unified_msg_origin)
        with open("msggroup.json", "w") as f:
            json.dump(msgg, f)
        
        yield event.plain_result("已设置该群组为开奖群组")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("getmsggroup")
    async def getmsggroup(self, event: AstrMessageEvent):
        with open("msggroup.json", "r") as f:
            msgg = json.load(f)
        chain = [
                Comp.Plain(f"{msgg}")
            ]
        yield event.chain_result(chain)
        
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("getwinlist")
    async def getwinlist(self, event: AstrMessageEvent):
        with open("getwinlist.json", "r") as f:
            mgetwinlist = json.load(f)
        chain = [
                Comp.Plain(f"{mgetwinlist}")
            ]
        yield event.chain_result(chain)
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("取消抽奖")
    async def stop(self, event: AstrMessageEvent):
        global task
        task.cancel()
        yield event.plain_result("已取消抽奖")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        #删除文件
        os.remove("code.json")
