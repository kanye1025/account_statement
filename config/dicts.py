from toolkit.utils.data_file import DataFile
head = "流水号/订单号,时间,收入,支出,备注/用途,余额/金额,对方账号,对方户名,收付款方式,开户机构/开户行,分类"
agent_dict = {"bank": "银行,bank", "alipay": "支付宝,alipay", "wechat": "微信,wechat"}
field_dict = {
    
    "bank_IE_type":            {
        "收支类型":   "收支,收/支,收支类型",
        "交易金额":   "金额,交易金额",
        "余额":     "余额,账户余额,余额",
        "对方账号":   "对方账号,卡号",
        "对方户名":   "对方户名,名称,账户名,收付款人,对方",
        "交易方式":"支付方式,交易方式",
        "交易类型":"交易类型,业务类型"
    },
    "bank_IE_sign":            {
        "交易金额":   "交易金额",
        "余额":     "账户余额",
        "对方账号":   "对方账号，卡号",
        "对方户名":   "对方户名,名称,账户名,收付款人,对方",
        "交易方式":"支付方式,交易方式",
        "交易类型":"交易类型,业务类型"
    },
    "bank_IE_split_debit_credit":{
        "支出":     "借方发生额",
        "收入":     "贷方发生额",
        "余额":     "余额,账户余额,交易余额",
        "对方账号":   "对方账号，卡号",
        "对方户名":   "对方户名,名称,账户名,收付款人,对方",
        "交易方式":"支付方式,交易方式",
        "交易类型":"交易类型,业务类型"
    },
    
    "bank_IE_split":    {
        "支出":     "支出,支出金额",
        "收入":     "收入,收入金额",
        "余额":     "余额,账户余额,交易余额",
        "对方账号":   "对方账号，卡号",
        "对方户名":   "对方户名,名称,账户名,收付款人,对方",
        "交易方式":"支付方式,交易方式",
        "交易类型":"交易类型,业务类型"
    },
    "bank_IE_role":            {
        "交易金额":   "交易金额,金额,收支金额",
        "余额":     "账户余额",
        "付款人":    "付款人,付款人名称",
        "收款人":    "收款人,收款人名称",
        "付款账号":   "付款账号,付款卡号",
        "收款账号":   "收款账号,收款卡号",
        "交易方式":"支付方式,交易方式",
        "交易类型":"交易类型,业务类型"
    },
    "bank":                    {
        "交易日期":   "交易日期",
        "交易金额":   "交易金额",
        "收支类型":   "收支类型，收/支",
        "余额":     "账户余额",
        "对方账号":   "对方账号",
        "对方户名":   "对方户名"
    },
    "wechat":                  {
        "交易类型":   "交易类型,类型",
        "收/支/其他": "收支类型，收/支",
        "交易方式":   "交易方式,方式,支付方式",
        "交易金额":   "交易金额,金额",
        "交易对方":   "交易对方,对方账户,对方户名",
    },
    "alipay":                  {
        "交易对方":   "交易对方",
        "商品说明":   "商品说明,备注,摘要",
        "收/付款方式": "收付款方式,支付方式,交易方式,资金渠道",
        "金额":     "交易金额,金额",
        "交易日期":   "交易日期",
    },
    "alipay_IE_type":          {
        "收/支":    "收支类型，收/支",
        "交易对方":   "交易对方",
        "商品说明":   "商品说明,备注,摘要",
        "收/付款方式": "收付款方式,支付方式,交易方式,资金渠道",
        "金额":     "交易金额,金额",
    },
    "alipay_IE_split":         {
        "收入":     "收入",
        "支出":     "支出",
        "商品说明":   "商品说明，备注,摘要",
        "收/付款方式": "收付款方式,支付方式,交易方式,资金渠道",
    }
}

for agent,d in field_dict.items():
    if 'bank_' in agent:
        d[f"备注1"] = "备注"
        d[f"备注2"] = "摘要"
        d[f"备注3"] = "说明"
        d[f"备注4"] = "附言"
        d[f"备注5"] = "用途"
       
field_code_name_dict = {
    "bank":{
        "trade_date":   "交易日期",
        "trade_amount":   "交易金额",
        "income_or_expenditure":   "收支类型",
        "remaining":       "余额",
        "reciprocal_account_num":   "对方账号",
        "reciprocal_account_name":   "对方户名"},
    "wechat":{
        "trade_date":   "交易日期",
        "trade_type":   "交易类型",
        "income_or_expenditure": "收/支/其他",
        "means_of_exchange":   "交易方式",
        "trade_amount":   "交易金额",
        "counterparty":   "交易对方"},
    "alipay":                  {
        "income_or_expenditure":       "收/支",
        "counterparty":    "交易对方",
        "trade_description":    "商品说明",
        "method_of_payment": "收/付款方式",
        "amount":        "金额",
        "trade_date":    "交易日期",
    },
}

bank_field_type_split = {
                       #"bank_IE_split_amount":["支出","收入"],
                       "bank_IE_type": ["收支","金额","余额"],
                       "bank_IE_sign":["金额,金额","余额"],
                       "bank_IE_split":["支出","收入","余额"],
                       "bank_IE_split_debit_credit":["借方发生额","贷方发生额","余额"],
                       "bank_IE_role":["付款","收款","金额","余额"]
                       }
alipay_field_type_split = {
                       "alipay_IE_type": ["收支","金额","余额"],
                       "alipay_IE_split":["收入","支出","余额"],
                       }

bank_field_type_join = {k:','.join(v) for k,v in bank_field_type_split.items()}
alipay_field_type_join = {k:','.join(v) for k,v in alipay_field_type_split.items()}

bank_code_dict = DataFile.load_str_dict("config/bank_code_dict.txt",split = '\t')

'''
account_label_dict = {
    "支出":
        {
            "应收":"投标保证金",
            "债权类资产":"借款",
            "储蓄类资产":"证券、基金",
            "处置类资产":"房产、汽车",
            "股权类资产":"资本金",
            "固定资产":"厂房、设备",
            "无形资产":"商标、专利",
            "应付":"退投标保证金、退保证金、贴息款、折让款、退餐费、退余款、退付保证金、退标、电票贴现放款、现汇折让、退社保预存款",
            "借款类负债":"还借款",
            "经营支出":"短信费、货款、字母+数字、培训费、服务、培训考试费用、采购付款、付款、改造款、玻渣款、锅炉部监检费、大庆炼化水冷壁集箱改造项目、安全措施费、食堂餐费、审图费用、手续费、税费扣缴、企业网银年服务费、探伤费、退餐费、房租；",
            "信贷支出":"利息",
            "消费支出":"水果、加油费、庆祝红包、餐饮消费、党费、电费、话费充值、停车费、购书、啤酒",
            "健康支出":"医疗类、人身保险理赔、诊所、药店",
            "娱乐支出":"游戏、打赏、主播、抖音",
            "其他支出":"其他"
        },
    "收入":
        {
            "应收":"退投标保证金、退保证金、贴息款、折让款、退餐费、退余款、退付保证金、退标、电票贴现放款、现汇折让",
            "应付":"付质保金、投标保证金、支付宝转账、财付通转账",
            "往来":"往来款、其他文案、空白文案、转账",
            "借款类负债":"借款",
            "经营收入":"货款、字母+数字、培训费、服务、培训考试费用、采购付款、付款、改造款、玻渣款",
            "营业外收入":"财政支付、探伤费、退餐费、房租、电费、补交款、投资收益、庆祝红包、佣金、退款",
            "实收资本":"资本金"
        }
}
'''
pay_type_dict = {
    "alipay":"收/支",
    "wechat": "收/支/其他",
    "bank":"收支类型"
}

accounting_entry_dict_ = {
    "减小":[
        "应收,收入","应付,支出","借款类负债,支出"
    ],
    "增加":[
        "应收,支出","债权类资产,支出","储蓄类资产,支出","处置类资产,支出","股权类资产,支出",
        "固定资产,支出","无形资产,支出","应付,收入","往来,收入","借款类负债,收入","经营支出,支出",
        "信贷支出,支出","消费支出,支出","健康支出,支出","娱乐支出,支出","其他支出,支出","经营收入,收入",
        "营业外收入,收入","实收资本,收入"
    ]
}

accounting_entry_dict = dict()

for accounting_entry,keys in accounting_entry_dict_.items():
    for k in keys:
        accounting_entry_dict[k] =accounting_entry
del accounting_entry_dict_


person_organization_dict = {
    "PERSON":"人名",
    "ORG":"公司,机构,组织,银行"
}