/**
 * 注册页面逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */

/**
 * 验证邮箱的是否有效
 * @param {String} email 邮箱字符串
 * @returns {boolean} true(合法邮箱)， false(非法邮箱)
 */
function validateEmail(email){
    var re = /^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$/;
    return re.test(email.toLowerCase());
}

/**
 * 显示错误消息
 * @param {String} msg 错误消息
 */
function showErrorMessage(msg){

    // 找到显示错误消息的标签
    var $alert = $accountForm.find(".uk-alert-danger");
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
function showFormLoading(isLoading){
    var $button = $accountForm.find('button');
    var $i = $accountForm.find('button[type=submit]').find('i');

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
function requestDone(data){
    // 如果有错则显示错误消息
    if (data.error){
        showFormLoading(false);
        showErrorMessage(data.message);
        return;
    }

    // 如果成功注册, 则定位到首页
    location.assign('/');
}

/**
 * 请求错误处理函数
 * @param xhr
 * @param status
 */
function requestFail(xhr, status){
    showFormLoading(false);
    showErrorMessage('网络出了问题 (HTTP '+ xhr.status+')');
}

/**
 * 提交账号信息
 * @param {Object} data 账号数据
 */
function postAccount(data){
    var opt = {
        type: 'POST',
        url: '/api/users',
        dataType: 'json',
        data: JSON.stringify(data || {}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(requestDone);
    jqxhr.fail(requestFail);
}

/**
 * 账号提交处理函数
 * @param event
 */
function accountSubmit(event){
    // 通知浏览器提交已被处理， 阻止默认行为的发生
    event.preventDefault();

    var name = $accountForm.find('#name').val();
    var email = $accountForm.find('#email').val();
    var password1 = $accountForm.find('#password1').val();
    var password2 = $accountForm.find('#password2').val();
    var verify = $accountForm.find('#verify-input').val();

    // 检查账号信息是否合法
    if (!name.trim()){
        showErrorMessage('请输入名字');
        return;
    }
    if (!validateEmail(email.trim().toLowerCase())) {
        showErrorMessage('请输入正确的Email地址');
        return;
    }
    if (password1.length < 6){
        showErrorMessage('密码长度至少为6个字符');
        return;
    }
    if (password1 !== password2){
        showErrorMessage('两次输入的密码不一致');
        return;
    }
    if (!verify.trim()){
        showErrorMessage('请输入验证码');
        return
    }

    showFormLoading(true);

    email = email.trim().toLowerCase();
    var account = {
        name: name.trim(),
        email: email,
        password: CryptoJS.SHA1(email + ':' + password1).toString(),
        verify: verify.trim()
    };

    // 将账号信息POST出去
    postAccount(account);
}

/**
 * 获取验证码图片结束处理函数
 * @param {Object} data 返回的数据
 */
function getVerifyImageRequestDone(data){
    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    $('#verify-image').attr('src', data.image)
}

/**
 * 发送获取验证码图片请求
 */
function getVerifyImageRequest(){
    var opt = {
        type: 'GET',
        url: '/api/verifyimage',
        dataType: 'json',
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(getVerifyImageRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 初始化页面
 */
function initPage(){
    window.$accountForm = $('#account-form');
    window.$accountForm.submit(accountSubmit);

    $accountForm.find('#new-image').click(function(){
        getVerifyImageRequest();
    });

    getVerifyImageRequest();
}


$(document).ready(initPage);