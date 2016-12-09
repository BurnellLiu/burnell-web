/**
 * 微博组件逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */

function weiboLogin() {
    var status = WB2.checkLogin();
    if (status){
        console.log(WB2.oauthData)
        WB2.anyWhere(function(W){
        //数据交互
        W.parseCMD('/users/show.json', function(oResult, bStatus) {
        if(bStatus) {
            console.log(oResult)
            }
        }, {
        uid : WB2.oauthData.uid
    }, {
        method : 'get',
        cache_time : 30
    });
});
        return;
    }

    WB2.login(function() {
    //callback function
});
}

function weiboLogout() {
    //alert('logout');
}
