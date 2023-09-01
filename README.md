# VE-CSRF-Defense

# 概述
对浏览器扩展进行的安全修改方案，以防御基于浏览器扩展无状态运行机制导致的跨站请求伪造攻击.
![alt](src/概括.pdf "修改示图")

# 用法
VE-CSRF-Defense对一个浏览器扩展包进行安全修改，在不影响其原始功能的情况下得到一个加固后的浏览器扩展包。

**拷贝代码**  
首先，你应该将我们的所有文件下载到你的linux系统中，可以使用git命令。

**下载浏览器扩展**  
其次，首先从Chrome扩展商城下载一个浏览器扩展包，.crx后缀类型的文件，将其放在“Extensions_test/扩展id/”，然后使用python运行src/
