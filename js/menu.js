// 获取头像和菜单栏元素
var userAvatar = document.getElementById('userAvatar');
var menuContainer = document.getElementById('menuContainer');

// 为头像添加点击事件监听器
userAvatar.addEventListener('click', function() {
    menuContainer.classList.toggle('open');
});