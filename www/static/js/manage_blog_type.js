
/**
 * 类别管理页面逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */


/**
 * 显示错误消息
 * @param {String} msg 错误消息, 如果设置为null, 则隐藏错误消息标签
 */
function showErrorMessage(msg){

    // 找到显示错误消息的标签
    var $error = $('#error');

    if (!msg){
        $error.text("cake");
        $error.css("visibility", "hidden");
        return;
    }

    $error.text(msg);
    $error.css("visibility", "visible");
}

/**
 * 设置数据是否处于加载状态
 * @param {Boolean} isLoading true(加载状态), false(非加载状态)
 */
function showDataLoading(isLoading){
    if (isLoading){
        $('#loading').css("visibility", "visible");
    }
    else {
        $('#loading').css("visibility", "hidden");
    }

}

/**
 * 设置表单提交是否处于加载状态
 * @param {Boolean} isLoading true(加载状态), false(非加载状态)
 */
function showButtonLoading(isLoading){
    var $button = $newTypeForm.find('button[type=submit]');
    var $i = $newTypeForm.find('button[type=submit]').find('i');

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
 * 上传博客类别请求结束处理函数
 * @param {Object} data 返回的数据
 */
function postBlogTypeRequestDone(data){
    showButtonLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    UIkit.modal.alert('增加博客类别成功!');

    var index = window.currentPageIndex;
    getBlogTypeRequest(index.toString());
}

/**
 * 提交博客类别
 * @param {Object} data 类别数据
 */
function postBlogType(data){

    showErrorMessage(null);
    showButtonLoading(true);

    var opt = {
        type: 'POST',
        url: '/api/blogtype',
        dataType: 'json',
        data: JSON.stringify(data || {}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(postBlogTypeRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 博客类别提交处理函数
 * @param event
 */
function newTypeSubmit(event) {
    // 通知浏览器提交已被处理， 阻止默认行为的发生
    event.preventDefault();

    var name = $newTypeForm.find('#type-name').val();
    var level = $newTypeForm.find('#type-level').val();

    if (!name.trim()) {
        showErrorMessage('请输入类别名称');
        return;
    }


    var blogType = {
        name: name.trim(),
        level: level
    };

    postBlogType(blogType);
}

/**
 * 删除博客类别请求结束处理函数
 */
function deleteBlogTypeRequestDone(data){
    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }
    // 如果成功删除博客类别, 则刷新页面
    var index = window.currentPageIndex;
    getBlogTypeRequest(index.toString());
}

/**
 * 发送删除博客类别请求
 * @param {String} typeId 博客类别Id
 */
function postDeleteBlogTypeRequest(typeId){
    var opt = {
        type: 'POST',
        url: '/api/blogtype/' + typeId + '/delete',
        dataType: 'json',
        data: JSON.stringify({}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(deleteBlogTypeRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 删除博客类别处理函数
 * @param {Object} e 标签对象
 */
function trashIConClicked(e){
    var id = $(e).attr('type-id');
    var name = $(e).attr('type-name');

    UIkit.modal.confirm('确认要删除"' + name + '"?删除后不可恢复!', function() {
        postDeleteBlogTypeRequest(id);
    });
}

/**
 * 跳页处理函数
 */
function jumpPageClicked(e){
    var num = $(e).attr('page');
    getBlogTypeRequest(num);
}

/**
 * 显示博客类别数据
 * @param {Object} data 博客类别数据
 */
function showTypeData(data){
    // 创建类别表
    var $table = $('#blog-type-table').find('tbody');
    // 先清空子节点
    $table.children('tr').remove();
    var types = data.types;
    for (var i in types){
        $table.append(
            '<tr >' +
            '<td>' +
            '<span>' + types[i].name + '</span>' +
            '</td>' +
            '<td class="uk-text-center">' + types[i].blog_count +
            '</td>' +
            '<td class ="uk-text-center">' + types[i].level +
            '</td>' +
            '<td class="uk-text-center">' +
            '<a onclick="trashIConClicked(this)" type-id="' + types[i].id + '" type-name="' + types[i].name + '">' +
            '<i class="uk-icon-trash-o"></i></a>' +
            '</td>' +
            '</tr>');
    }
    // 少于10行的填充空白
    for (i = 0; i < 10-types.length; i++){
        $table.append('<tr><td>&nbsp</td><td></td><td></td><td></td></tr>');
    }

    // 创建分页列
    var $ul = $('ul.uk-pagination');
    // 先清空子节点
    $ul.children('li').remove();

    var currentIndex = data.page.page_index;
    var pageCount = data.page.page_count;

    var previousLi = null;
    if (data.page.has_previous){
        var pageIndex = currentIndex-1;
        previousLi = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)">' +
            '<i class="uk-icon-angle-double-left"></i></a></li>'
    }
    else {
        previousLi = '<li class="uk-disabled"><span><i class="uk-icon-angle-double-left"></i></span></li>';
    }
    $ul.append(previousLi);

    if ((currentIndex - 4) > 0){
        var li = '<li><a page="1" onclick="jumpPageClicked(this)"><span>1</span></a></li><li><span>...</span></li>';
        $ul.append(li);
    }

    if ((currentIndex - 4) === 0){
        li = '<li><a page="1" onclick="jumpPageClicked(this)"><span>1</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex - 2) > 0){
        pageIndex = currentIndex-2;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex - 1) > 0){
        pageIndex = currentIndex-1;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    $ul.append('<li class="uk-active"><span>' + currentIndex + '</span></li>');

    if ((currentIndex + 1) <= pageCount){
        pageIndex = currentIndex+1;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex + 2) <= pageCount){
        pageIndex = currentIndex+2;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex + 3) === pageCount){
        pageIndex = currentIndex+3;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex + 3) < pageCount){
        li = '<li><span>...</span></li><li><a page="' + pageCount +'" onclick="jumpPageClicked(this)"><span>' + pageCount +'</span></a></li>';
        $ul.append(li);
    }

    var nextLi = null;
    if (data.page.has_next){
        pageIndex = currentIndex + 1;
        nextLi = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)">' +
            '<i class="uk-icon-angle-double-right"></i></a></li>';
    }
    else {
        nextLi = '<li class="uk-disabled"><span><i class="uk-icon-angle-double-right"></i></span></li>';
    }
    $ul.append(nextLi);
}

/**
 * 获取博客类别请求结束处理函数
 * @param {Object} data 返回的数据
 */
function getBlogTypeRequestDone(data){
    showDataLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    window.currentPageIndex = data.page.page_index;
    showTypeData(data);
}

/**
 * 请求错误处理函数
 * @param xhr
 * @param status
 */
function requestFail(xhr, status){
    showButtonLoading(false);
    showDataLoading(false);
    showErrorMessage('网络出了问题 (HTTP '+ xhr.status+')');
}

/**
 * 发送获取博客类别请求
 * @param {String} pageIndex 页面索引
 */
function getBlogTypeRequest(pageIndex){

    showErrorMessage(null);
    showDataLoading(true);

    var opt = {
        type: 'GET',
        url: '/api/blogtype?page=' + pageIndex,
        dataType: 'json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(getBlogTypeRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 初始化页面
 */
function initPage(){
    window.$newTypeForm = $('#new-type-form');
    window.$newTypeForm.submit(newTypeSubmit);
    getBlogTypeRequest('1');
}

$(document).ready(initPage);
