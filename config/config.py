class CONF:
    '''
    embeding_model_path = "./text2vec-large-chinese"
    GPU = True
    '''
    
    embeding_model_path = "../../models/text2vec-large-chinese"
    #llm_model_path = "../../chatglm2-6b-int4"
    #llm_model_path = "../../chatglm3-6b"
    #llm_model_path = "../../Baichuan2-7B-Chat-4bits"
    llm_model_path = "../../models/Baichuan2-13B-Chat-4bits"
    #llm_model_path = "../../models/Baichuan2-13B-Chat"
    GPU = True
    recog_info_embeding_path = './model/recog_info_embeding.bin'
    load_embeding = True
    max_worker = 1
    
    