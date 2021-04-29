运行平台为python3.7，anaconda3
请按照requirement.txt配置环境

环境配置完毕后，运行python main_proc/main.py打开程序
各文件功能介绍如下：
keda_tingxie.sub_instruction # 语音听写模块
gene_voice.speak_word        # 语音合成模块
UNIT.baidu_chat                  # UNIT语音平台引入
bilibili.bilibili_search              # B站视频模块引入
QQ_chat.qq_program           # QQ聊天相关程序调用
visual_scene.yolo_detect_obj # yolo实时检测引入
visual_scene.image_detect    # 百度平台通用物体和场景识别引入
注意：
1，QQ登录功能需要在函数QQ()中传入账号和密码
2，yolo模块的cfg文件和weights文件在使用时应该为绝对路径，否则无法使用