# 项目

线上目录: /share/home/ds/chatbot_api

## 线上环境

1. 服务器：webserver23

2. 日志:
   - /data/var/log/chatbot_api.log.stderr
   - /data/var/log/chatbot_api.log.stdout

3. 启动：
   ds账号运行 `./run.sh`

接口说明：<https://chatgpt.mktindex.com/docs>

1. gpt_openai
openai官方接口，支持输入openai模型名称，推荐使用

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/gpt_openai', 
    data=json.dumps({'text': '1+1=?', 'model':"gpt-4-1106-preview"}), 
    verify=False
)
```

2. gpt_openai2
第三方提供的接口，支持输入openai模型名称，推荐使用

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/gpt_openai2', 
    data=json.dumps({'text': '1+1=?', 'model':"gpt-4-1106-preview"}), 
    verify=False
)
```

3. chatbot
gpt3.5

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/chatbot', 
    data=json.dumps({'text': '1+1=?', 'OPENAI_API_KEY':""}), 
    verify=False
)
```

4. gpt4
gpt4

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/gpt4', 
    data=json.dumps({'text': '1+1=?', 'OPENAI_API_KEY':""}), 
    verify=False
)
```

5. vec
向量化

```python
res = requests.post(
    url='https://chatgpt.mktindex.com/vec', 
    data=json.dumps({'text': '可乐', 'OPENAI_API_KEY':""}), 
    verify=False
)
```
