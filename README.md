# ime-savior
## windows11 第三方输入法救星

windows11 一旦启用过触摸键盘，使用第三方输入法时，会出现恶心的bug。举例：随意复制一段文字后再用第三方输入法进行输入，首字母必定是英文。

每次开机开启一次触摸键盘，该 Bug 就不会出现，但是每次重启后，都会出现。也就是说每次开机都要打开一次触摸键盘。

我写了这个工具，运行它会在一秒钟内打开和关闭触摸键盘。将其或其快捷方式添加到启动文件夹。这样每次重启后，输入法就正常了。程序的实现是打开触摸键盘，1秒后关闭触摸键盘。开机自启动时偶尔自动关闭会失效，此时请手动关闭触摸键盘即可。