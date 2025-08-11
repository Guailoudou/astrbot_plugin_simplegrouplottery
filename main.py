from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import os,json,random
@register("getcode", "Guailoudou", "一个简单的 GET 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("参与抽奖")
    async def addqq(self, event: AstrMessageEvent):
        """这是一个 get 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
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

    # @filter.command("getfile")
    # async def getfile(self, event: AstrMessageEvent):
    #     """获取数据文件"""
    #     chain = [
    #         Comp.File(file="code.json", name="code.json")
    #     ]
    #     yield event.chain_result(chain)

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
    @filter.command("开始抽奖")
    async def start(self, event: AstrMessageEvent):
        with open("code.json", "r") as f:
            code = json.load(f)
        length = len(code)
        num = random.randint(0, length - 1)
        info = list(code.items())[num]
        chain = [
            Comp.At(qq=info[0]), # At 消息发送者
            Comp.Plain("恭喜你中奖了"),
            #中奖信息
            Comp.Plain(f"用户名：{info[1]}"),
        ]
        yield event.chain_result(chain)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
