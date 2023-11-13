from transformers import AutoModel

#model = AutoModel.from_pretrained("../../chatglm3-6b",trust_remote_code=True).quantize(4)
#model.save_pretrained("../../chatglm3-6b-4bit")
model = AutoModel.from_pretrained("../../chatglm3-6b-4bit",trust_remote_code=True)