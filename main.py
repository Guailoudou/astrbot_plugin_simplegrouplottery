from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
import os,json
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
        message_str = event.message_str # 用户发的纯文本消息字符串
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
        else:
            code[qq] = user_name
            with open("code.json", "w") as f:
                json.dump(code, f)

        yield event.plain_result(f"{os.getcwd()}, 你发了 {message_str}!  {message_obj.sender.user_id}") # 发送一条纯文本消息

    @filter.command("getfile")
    async def getfile(self, event: AstrMessageEvent):
        """获取数据文件"""
        chain = [
            Comp.File(file="code.json", name="code.json")
        ]
        yield event.chain_result(chain)

    @filter.command("getqqs")
    async def getqqs(self, event: AstrMessageEvent):
        """获取QQ列表"""
        with open("code.json", "r") as f:
            code = json.load(f)
            chain = [
                Comp.Plain(f"{code}")
            ]
        yield event.chain_result(chain)

    @filter.command("rmqq")
    async def rmqq(self, event: AstrMessageEvent, qq: int):
        """删除QQ"""
        with open("code.json", "r") as f:
            code = json.load(f)
            if qq not in code:
                chain = [
                    Comp.Plain("QQ不存在")
                ]
                yield event.chain_result(chain)
                return
        code.remove(qq)
        with open("code.json", "w") as f:
            json.dump(code, f)
        yield event.chain_result([Comp.Plain("删除成功")])

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
