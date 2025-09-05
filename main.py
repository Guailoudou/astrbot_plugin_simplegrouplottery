from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult,MessageChain
from astrbot.api.star import Context, Star, register,StarTools
from astrbot.api import logger
import astrbot.api.message_components as Comp
import os,json,random,time,asyncio
@register("simplegrouplottery", "Guailoudou", "一个简单的 群抽奖 插件", "1.0.0")
class LotteryPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data_dir = StarTools.get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.qqs_file = self.data_dir / r"qqs.json"
        self.group_file = self.data_dir / r"msggroup.json"
        self.task_file = self.data_dir / r"task.json"
        self.winlist_file = self.data_dir / r"winlist.json"
        self.qqs_data = {}
        self.group_data = []
        self.task_data = []
        self.winlist_data = []
        # self.task = None

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        await self.init()
        self.task = asyncio.create_task(self.tick())
        logger.info("插件初始化完成")
    
    async def init(self):
        """数据初始化"""
        if not self.qqs_file.exists():
            with open(self.qqs_file, "w") as f:
                json.dump({}, f)
        if not self.group_file.exists():
            with open(self.group_file, "w") as f:
                json.dump([], f)
        if not self.task_file.exists():
            with open(self.task_file, "w") as f:
                json.dump({}, f)
        if not self.winlist_file.exists():
            with open(self.winlist_file, "w") as f:
                json.dump([], f)
        with open(self.qqs_file, "r") as f:
            self.qqs_data = json.load(f)
        with open(self.group_file, "r") as f:
            self.group_data = json.load(f)
        with open(self.task_file, "r") as f:
            self.task_data = json.load(f)
        with open(self.winlist_file, "r") as f:
            self.winlist_data = json.load(f)
    async def save(self,type:str):
        """数据保存"""
        if(type == "qqs"):
            with open(self.qqs_file, "w") as f:
                json.dump(self.qqs_data, f)
        if(type == "group"):
            with open(self.group_file, "w") as f:
                json.dump(self.group_data, f)
        if(type == "task"):
            with open(self.task_file, "w") as f:
                json.dump(self.task_data, f)
        if(type == "winlist"):
            with open(self.winlist_file, "w") as f:
                json.dump(self.winlist_data, f)
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("joinLottery", alias={'参与抽奖', '参加抽奖'})
    async def addqq(self, event: AstrMessageEvent):
        """参加""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        # message_str = event.message_str # 用户发的纯文本消息字符串
        message_obj = event.message_obj # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        
        qq = message_obj.sender.user_id

        if event.unified_msg_origin not in self.group_data:
            yield event.plain_result("你没有参与抽奖的权限或不符合参与条件")
            return

        if qq in self.qqs_data:
            yield event.plain_result("你已经申请过参与抽奖了，请勿重复参与")
            return
        else:
            self.qqs_data[qq] = user_name
            await self.save("qqs")
        if self.task is not None:
            logger.info("当前存在正在执行的任务")
        yield event.plain_result(f"用户{message_obj.sender.user_id}参与成功\n请注意查看参与规则：https://qr18.cn/BFqYTX") # 发送一条纯文本消息

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_getqqs")
    async def getqqs(self, event: AstrMessageEvent):
        """获取QQ列表"""
        chain = [
            Comp.Plain(f"参与人数：{len(self.qqs_data)} \n详细信息{self.qqs_data}")
        ]
        yield event.chain_result(chain)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_rmqq")
    async def rmqq(self, event: AstrMessageEvent, qq: str):
        """删除QQ"""
        code = self.qqs_data
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
        await self.save("qqs")
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_rmgroup")
    async def rmgroup(self, event: AstrMessageEvent):
        """删除all开奖源群"""
        self.group_data.clear()
        await self.save("group")
        yield event.chain_result([Comp.Plain("删除成功")])

    async def tick(self):
        """隔1s检查一次是否有过时间但未激活的任务"""
        await asyncio.sleep(2)
        while True:
            for i in self.task_data:
                if not i["runned"] and i["start"]:           
                    newtime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                    newtime = int(newtime)
                    if i["time"] < newtime:
                        logger.info("开始执行任务")
                        i["runned"] = True
                        i['start'] = False
                        await self.Lotterystart(self)
                        await self.save("task")
            await asyncio.sleep(1)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_addgroup")
    async def addgroup(self,event: AstrMessageEvent):
        """添加开奖源群"""
        self.group_data.append(event.unified_msg_origin)
        await self.save("group")
        yield event.plain_result("已设置该群组为开奖群组")


    # async def timeout(self, event: AstrMessageEvent,times: int):
    #     try:
    #         await asyncio.sleep(times)
    #     except asyncio.CancelledError:
    #         chain = event.chain_result([Comp.Plain(f"已取消抽奖")])
    #         with open("msggroup.json", "r") as f:
    #             msgg = json.load(f)
    #         for i in msgg:
    #             await self.context.send_message(i,event.chain_result(chain))
    #         if event.unified_msg_origin not in msgg:
    #             await self.context.send_message(event.unified_msg_origin,event.chain_result(chain))
    #         return
    #     logger.info("已等待{}秒".format(times))
    #     await LotteryPlugin.Lotterystart(self, event)
    #     # yield event.chain_result([Comp.Plain(f"1开始等待{times}秒")])
    #     # await asyncio.sleep(times)
    #     # yield event.chain_result([Comp.Plain(f"已等待{times}秒")])
    #     # task = asyncio.create_task(timed_task(event,times))
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("开始抽奖")
    async def Lotterystart(self,event: AstrMessageEvent = None,name:str = ""):
        logger.info("开始抽奖")
        # yield event.chain_result([Comp.Plain(f"将在{times}秒")])
        # await asyncio.sleep(times\
        code = self.qqs_data
        length = len(code)
        num = random.randint(0, length - 1)
        info = list(code.items())[num]
        data = self.task_data.get(name)
        chain = [
            Comp.At(qq=info[0]), 
            Comp.Face(id=144),
            Comp.Plain(f"恭喜你中奖了"),
            Comp.Face(id=144),
            Comp.Plain(f"\n"),
            Comp.Plain(f" \n中奖信息：\nQQ号：{info[0]}\n用户名：{info[1]}\n奖品：{data['gift']}\n请于48小时内联系管理员领取奖品，具体领取方式请查看活动信息\n{data['rule']}"),
            Comp.Image.fromURL(data["imgurl"]),
        ]
        winlist = self.winlist_data
        winlist.append({
            "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            "info": info
        })
        await self.save("winlist")

        msgg = self.group_data
        for i in msgg:
            await self.context.send_message(i,MessageChain(chain))
        


    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("启动抽奖")
    async def timestart(self, event: AstrMessageEvent,name:str):
        # times = 20250903200000
        data = self.task_data.get(name)
        if not data:
            yield event.plain_result("未找到该任务")
        
        times_str = str(data["time"])
        times_str_gsh = times_str[0:4]+"年"+times_str[4:6]+"月"+times_str[6:8]+"日"+times_str[8:10]+"时"+times_str[10:12]+"分"+times_str[12:14]+"秒"
        chain = [
            Comp.Plain(f"{data["info"]}将于{times_str_gsh}开奖\n参与方式：发送 /参与抽奖 \n奖品：{data["gift"]}\n具体领取方式请查看活动信息\n{data["rule"]}"),
            Comp.Image.fromURL(data["imgurl"]),
        ]

        data["start"] = True
        data["runned"] = False

        self.save("task")

        msgg = self.group_data
        for i in msgg:
            await self.context.send_message(i,event.chain_result(chain))
        if event.unified_msg_origin not in msgg:
            await self.context.send_message(event.unified_msg_origin,event.chain_result(chain))
        event.stop_event()
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_new")
    async def new(self, event: AstrMessageEvent,name:str,time:int = 0,info:str = "",rule:str = "",gift:str = "",imgurl:str = ""):
        """新建抽奖活动"""
        data = {
            "id": name,
            "time": time,
            "info": info,
            "imgurl": imgurl,
            "rule": rule,
            "gift": gift,
            "start": False,
            "runned": False
        }
        self.task_data[name] = data
        await self.save("task")
        yield event.plain_result(f"已成功参加新的抽奖活动：{name}，相关数据：\n{data}")
        event.stop_event()

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_set")
    async def set_time(self, event: filter.Event, name: str, type:str ,info: str):
        data = self.task_data.get(name)
        if not data: 
            yield event.plain_result(f"未找到名为{name}的抽奖活动")
            return
        if(type == "time"): info = int(info)
        data[name][type] = info
        await self.save("task")
        yield event.plain_result(f"已设置{name}的{type}为{info}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_get")
    async def lt_get(self, event: filter.Event):
        yield event.plain_result(f"当前所有活动：{self.task_data}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("lt_getmsggroup")
    async def getmsggroup(self, event: AstrMessageEvent):
        """获取开奖群组"""
        msgg = self.group_data
        chain = [
                Comp.Plain(f"{msgg}")
            ]
        yield event.chain_result(chain)
        
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("getwinlist")
    async def getwinlist(self, event: AstrMessageEvent):
        """获取中奖名单"""
        winlist = self.winlist_data
        chain = [
                Comp.Plain(f"{winlist}")
            ]
        yield event.chain_result(chain)
    
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("取消抽奖")
    async def stop(self, event: AstrMessageEvent):
        """取消抽奖"""
        # task = LotteryPlugin.task
        if len(self.task_data) == 0:
            yield event.plain_result("没有进行中的抽奖")
            return
        self.task_data = []
        await self.save("task")
        yield event.plain_result("已取消抽奖")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        await self.task.cancel()
        self.task = None
        
