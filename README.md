# `ime-savior`：Windows 11 输入法救星
Windows 11 一旦启用过触摸键盘，使用输入法时会出现难以描述的问题：原理上，首字母似乎会进入字符组合状态，呈现出类似已经上屏的英文的样貌，但带有虚线。该问题导致嗣后键入的文字全都不能上屏。复现方法十分简单，任意一处复制任意内容后，再使用输入法输入，首字母必定如此。

若你永远用不上开启触摸键盘，比如使用台式机，修复方法是：在注册表 `HKEY_CURRENT_USER\Software\Microsoft\InputMethod\Settings\Common` 中把 `TouchKeyboardHasEverShown` 设为 `0`，并且今后也不要再打开触摸键盘。

```powershell
reg add "HKCU\Software\Microsoft\InputMethod\Settings\Common" /v TouchKeyboardHasEverShown /t REG_DWORD /d 0 /f
```

如果你对触摸键盘仍有时不时的需求，或者无法避免在个别情况下启用它，那么每次启动 `explorer.exe` 后，开启一次触摸键盘，该问题就不会出现。

为了简化这一流程，可以使用本工具。运行它会在每次 `explorer.exe` 变化（例如开机、重新运行）后，半秒钟内接连打开、关闭触摸键盘。将它添加到启动文件夹，这样输入法就始终正常了。

其原理是每半秒钟检查 `explorer.exe` 情况。程序由 GPT-6.1 Sol 歪伯而来，是否造成资源泄漏暂时未知。据报，软键盘的自动关闭可能失效。
## 参考
1. 百度贴吧：[中文状态下第一个字母是英文](https://tieba.baidu.com/p/6241077887) 着重感谢本贴 @yoyoLumi @王兰花秀丽♡ 的回答
2. 微软文档：[组合字符](https://learn.microsoft.com/en-us/windows/win32/tsf/compositions)
3. 微软社区：[Windows11 24H2开启触摸键盘功能后，会导致输入法首字母不被自定义输入法接管（变为英文）](https://learn.microsoft.com/zh-cn/answers/questions/3971899/windows11-24h2)
4. 小狼毫议题：[ctrl+c之后，rime出现奇怪的上屏问题](https://github.com/rime/weasel/issues/1519#issuecomment-2880862406)
