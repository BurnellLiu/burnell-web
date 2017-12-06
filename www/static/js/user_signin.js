/**
 * 登录页面逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */

/**
 * 显示错误消息
 * @param {String} msg 错误消息, 如果为null则清除错误消息
 */
function signinShowErrorMessage(msg){

    // 找到显示错误消息的标签
    var $alert = $signinAccountForm.find(".uk-alert-danger");
    if ($alert.length === 0){
        return;
    }

    if (!msg){
        $alert.text('');
        $alert.addClass('uk-hidden');
        return;
    }

    $alert.text(msg);
    $alert.removeClass('uk-hidden');
}

/**
 * 设置表单是否处于加载状态
 * @param {Boolean} isLoading true(加载状态), false(非加载状态)
 */
function signinShowFormLoading(isLoading){
    var $button = $signinAccountForm.find('button');
    var $i = $signinAccountForm.find('button[type=submit]').find('i');

    if (isLoading) {
        $button.attr('disabled', 'disabled');
        $i.addClass('uk-icon-spinner').addClass('uk-icon-spin');
    }
    else {
        $button.removeAttr('disabled');
        $i.removeClass('uk-icon-spinner').removeClass('uk-icon-spin');
    }
}

/**
 * 请求结束处理函数
 * @param {Object} data 返回的数据
 */
function signinRequestDone(data){

    // 如果有错则显示错误消息
    if (data.error){
        signinShowFormLoading(false);
        signinShowErrorMessage(data.message);
        return;
    }

    var path = window.location.pathname;
    if (path === '/register'){
        location.assign('/');
    }
    else {
        // 如果成功登录, 则刷新当前页面
        location.reload();
    }

}

/**
 * 请求错误处理函数
 * @param xhr
 * @param status
 */
function signinRequestFail(xhr, status){
    signinShowFormLoading(false);
    signinShowErrorMessage('网络出了问题 (HTTP ' + xhr.status + ')' + '(' + status + ')');
}


/**
 * 提交账号信息
 * @param {Object} data 账号数据
 */
function signinPostAccount(data){
    var opt = {
        type: 'POST',
        url: '/api/authenticate',
        dataType: 'json',
        data: JSON.stringify(data || {}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    //noinspection JSUnresolvedFunction
    jqxhr.done(signinRequestDone);
    //noinspection JSUnresolvedFunction
    jqxhr.fail(signinRequestFail);
}


/**
 * 账号提交处理函数
 * @param event
 */
function signinAccountSubmit(event){
    // 通知浏览器提交已被处理， 阻止默认行为的发生
    event.preventDefault();

    signinShowFormLoading(true);

    var email = $signinAccountForm.find("#email").val();
    email = email.trim().toLowerCase();

    var password = $signinAccountForm.find("#password").val();

    var account = {
        email: email,
        password: CryptoJS.SHA1(email + ':' + password).toString()
    };

    // 将账号信息POST出去
    signinPostAccount(account);
}

/**
 * 初始化页面
 */
function signinInitPage(){
    window.$signinAccountForm = $("#sign-in-account-form");
    window.$signinAccountForm.submit(signinAccountSubmit);
}


$(document).ready(signinInitPage);
