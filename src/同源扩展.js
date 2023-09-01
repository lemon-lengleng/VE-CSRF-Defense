//console.log("???");
//异步处理方法，每次tab url变化之后先移除上一个监听函数
var tab_url;	//定义全局变量tab_url，记录当前页面url。

chrome.tabs.onActivated.addListener( function(activeInfo){	//切换标签页可以检测，但是手动输入标签页url不行
    chrome.tabs.get(activeInfo.tabId, function(tab){
        tab_url = tab.url;
        console.log("you are here切换: "+tab_url);
    });
});

chrome.tabs.onUpdated.addListener((tabId, change, tab) => {	//在同一个tab下改变url可以捕捉到，但是切换tab捕捉不到
    if (tab.active && change.url) {
		tab_url = change.url;
        console.log("you are here，改变: "+change.url);
    }
});

function csrf(){	//发起CSRF攻击，用于验证是否会被拦截
	console.log("csrf");
	var xhr = new XMLHttpRequest();
	xhr.open("GET", "http://127.0.0.1/vulnerabilities/csrf/?password_new=123&password_conf=123&Change=Change#",true);
	xhr.onreadystatechange=function(){
	// 在监听xhr的请求状态 readyState为4代表请求成功，status为200代表响应成功
		console.log(xhr.readyState);
	}
	xhr.send();
}

function Listening_requests(){	//加载监听请求函数，监听网站所有请求
	console.log("dangqiantaburl:"+tab_url);
	chrome.webRequest.onBeforeSendHeaders.addListener(	//拦截请求
	  beforeSendHeadersListener,
	  {urls: ["<all_urls>"]},
	  ["blocking","requestHeaders","extraHeaders"]	//一定要加上"requestHeaders"，不然读取不到details.requestHeaders。
	);												//一定要加上"extraHeaders",不然提取不到cookie，这个整了好久
}

function isSameOrigin(url1, url2) {	//比较两个url是否同源
  // 创建两个 URL 对象
  var parsedUrl1 = new URL(url1);
  var parsedUrl2 = new URL(url2);

  // 比较协议、主机和端口号
  if (
    parsedUrl1.protocol === parsedUrl2.protocol &&
    parsedUrl1.hostname === parsedUrl2.hostname &&
    parsedUrl1.port === parsedUrl2.port
  ) {
    return true; // 两个 URL 同源
  } else {
    return false; // 两个 URL 不同源
  }
}

var beforeSendHeadersListener = function(details){	//异步处理函数，获取到的请求url和当前tab函数作比较，看是否同源，不同源就去除请求cookie
	console.log("是否同源:"+isSameOrigin(details.url,tab_url));
	console.log("tab_url:"+tab_url);
	console.log("请求url:"+details.url);
	console.log("details:"+JSON.stringify(details));
		if(!isSameOrigin(details.url,tab_url)){	//不是同源策略就去除cookie
			for (var i = 0; i < details.requestHeaders.length; ++i) {
				  if (details.requestHeaders[i].name.toLowerCase() === 'cookie') {
					// 将请求头中的 Cookie 设置为空字符串
					console.log("去除cookie");
					details.requestHeaders.splice(i,1);
					break;
				  }
				}
				return { requestHeaders: details.requestHeaders };
		}
		
		return { requestHeaders: details.requestHeaders };
}

Listening_requests();		//开启监听

setTimeout(()=>{
    //csrf();	//CSRF攻击
  },4000);	


//删除字符串中某个字符及其后面的所有字符
function deleteAfterCharacter(str, character) {
  const index = str.indexOf(character);
  if (index !== -1) {
    return str.slice(0, index);
  }
  return str;
}
