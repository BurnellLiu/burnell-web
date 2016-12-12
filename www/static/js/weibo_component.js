/**
 * 微博组件逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */

/**
 * 请求结束处理函数
 * @param {Object} data 返回的数据
 */
function requestDone(data){
    if (data.error){
        return;
    }

    var url = location.pathname;
    location.assign(url);
}

/**
 * 请求错误处理函数
 * @param xhr
 * @param status
 */
function requestFail(xhr, status){
    console.log('网络出了问题 (HTTP ' + xhr.status + ')' + '(' + status + ')');
}

/**
 * 提交微博账号信息
 * @param {Object} data 账号数据
 */
function postWeiboAccount(data){
    var opt = {
        type: 'POST',
        url: '/api/weibo/login',
        dataType: 'json',
        data: JSON.stringify(data || {}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    //noinspection JSUnresolvedFunction
    jqxhr.done(requestDone);
    //noinspection JSUnresolvedFunction
    jqxhr.fail(requestFail);
}

/**
 * 微博登录处理函数
 */
function weiboLogin() {
    var status = WB2.checkLogin();
    if (status){
        var account = {
            uid: WB2.oauthData.uid,
            access_token: WB2.oauthData.access_token
        };
        postWeiboAccount(account);
    }
    else {
        WB2.login(function() {
            var account = {
                uid: WB2.oauthData.uid,
                access_token: WB2.oauthData.access_token
            };
            postWeiboAccount(account);
        });
    }


}

