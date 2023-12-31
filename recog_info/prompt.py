from toolkit.ml.llm.prompt_base import PromptBase

class Prompts(PromptBase):
    FIELD_PROMPT = """
给出一份银行流水:
【
{text}
】
请从上述流水中提取相关字段并以如下json格式返回：
```{
"交易日期":"",
"当前账户":{"开户行":"","账号":"","户名":""},
"交易对手账户":{"开户行":"","账号":"","户名":""},
"备注/摘要/附言/说明":[""],
"交易金额":0.0,
"收支类型":"",
"余额":0.0 或 "",
"订单类型":"",
"交易网点":"",
"交易渠道":"",
"交易类型":"",
"交易方式":""
}```
以上字段与流水中并非一一对应，需要理解并推理获得相关信息
其中只有收入金额，则收支类型为收入，只有支出金额则收支类型为支出，交易日期可以从交易时间中提取，为'yyyy-MM-dd'格式
不能识别的字段就返回空
"""

    account_label_prompt = """已知交易流水的类型标签和说明（格式为 标签类型-->标签说明）：
{des}
请判断下列交易流水信息的标签类型，并返回如下json
```{
"标签类型":""
}```
取值只能为{key}中的一个,
以下为流水信息
【
{text}
】
"""

    consume_label_prompt = """已知消费类型定义（格式为 类型标签-->类型说明）：
{des}
请从下列消费信息中判断消费的类型，并返回如下json
```{
"消费类型":""
}```
取值只能为{key}中的一个,不能识别的,就返回"消费_其他服务"
消费信息：
{text}
"""



    income_or_expenses_prompt = """请根据流水信息判断该流水是一笔支出，还是一笔收入，
并返回如下json
```{
"收支类型":""
}```
取值只能为["支出","收入",""]中的一个,
流水信息：
{text}
"""