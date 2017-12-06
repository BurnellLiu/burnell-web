/**
 * 第三方登陆逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */

/**
 * 登出处理函数
 */
function logout() {
    location.assign('/signout');
}

/**
 * GitHub登陆处理函数
 */
function githubLogin(e) {
    // 转到GitHub登陆页面
    var clientID = $(e).attr('clientid');
    var redirectUri = $(e).attr('redirecturi');
    var url = 'https://github.com/login/oauth/authorize?client_id=';
    url += clientID;
    url += '&redirect_uri=';
    url += redirectUri;
    url += '&state=';
    url += location.pathname;
    url += location.search;

    location.assign(url);
}

