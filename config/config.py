class CONF:
    
    embeding_model_path = "../../text2vec-large-chinese"
    llm_model_path = "../../chatglm2-6b-int4"
    GPU = True
    """
    embeding_model_path = "./text2vec-large-chinese"
    llm_model_path = "./chatglm2-6b-int4"
    GPU = False
    """
    
    recog_info_embeding_path = './model/recog_info_embeding.bin'
    load_embeding = True
    max_worker = 8