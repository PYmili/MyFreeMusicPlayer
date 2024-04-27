document.addEventListener('DOMContentLoaded', function() {
    var audio = new Audio(); // 创建音频对象
    var isPlaying = false; // 播放状态标志
    var progressBar = $('#progressBar')[0]; // 获取进度条元素
    var volumeBar = $('#volumeBar')[0]; // 获取音量调节条元素
    var musicList = $('#musicList ul li'); // 获取音乐列表
    var repeatButton = $('#repeatButton'); // 获取重复播放按钮

    function clearSelection() {
        $('#musicList ul li').removeClass('active');
    }

    // 在播放音乐时更新音乐信息显示
    audio.onplay = function() {
        var currentSong = $('#musicList ul li.active').text();
        $('#musicInfo').text(currentSong);
    };

    // 播放/暂停按钮点击事件
    $('#playPauseButton').on('click', function() {
        if (!isPlaying) { // 如果当前未播放音乐，则开始播放
            console.log('开始播放音乐');
            var firstMusicSrc = document.querySelector('#musicList ul li.active').getAttribute('data-src');
            console.log("获取data-src: " + firstMusicSrc);
            if (!audio.src && firstMusicSrc) {
                audio.src = firstMusicSrc;
                musicList.first().addClass('active'); // 添加选中效果
            }
            if (!isNaN(audio.duration) && isFinite(audio.duration) && audio.duration !== 0) {
                audio.currentTime = (progressBar.value * audio.duration) / 100; // 设置音频播放位置
            }
            console.log("播放音乐：" + audio.src);
            audio.play();
            isPlaying = true;
            // 切换按钮图标
            $('#playPauseButton').removeClass("icon-bofang");
            $('#playPauseButton').addClass("icon-zanting");
        } else { // 如果当前正在播放音乐，则暂停
            console.log('暂停播放音乐');
            audio.pause();
            isPlaying = false;
            // 切换按钮图标
            $('#playPauseButton').removeClass("icon-zanting");
            $('#playPauseButton').addClass("icon-bofang");
        }
    });

    // 重复播放按钮点击事件
    repeatButton.on('click', function() {
        if (audio.loop) {
            audio.loop = false;
            console.log("按顺序播放");
            $(this).removeClass("icon-danxunhuan");
            $(this).addClass("icon-duoxunhuan");
        } else {
            audio.loop = true;
            console.log("单曲循环");
            $(this).removeClass("icon-duoxunhuan");
            $(this).addClass("icon-danxunhuan");
        }
    });

    // 音乐播放结束事件
    audio.onended = function() {
        console.log('音乐播放结束');
        if (!audio.loop) { // 如果未设置为重复播放，则自动跳转到列表中的下一首音乐
            var nextMusic = $('#musicList ul li.active').next();
            if (nextMusic.length > 0) { // 检查是否存在下一首音乐
                audio.src = nextMusic.data('src');
                nextMusic.addClass('active').siblings().removeClass('active'); // 设置选中效果
                audio.play();
            } else {
                // 如果没有下一首音乐，停止播放并重置播放状态
                audio.pause();
                audio.currentTime = 0;
                isPlaying = false;
                $('#playPauseButton').removeClass("icon-zanting");
                $('#playPauseButton').addClass("icon-bofang");
            }
        }
    };

    // 更新播放进度条
    audio.ontimeupdate = function() {
        var progress = (audio.currentTime / audio.duration) * 100;
        progressBar.value = progress;
    };

    // 更新音量调节条
    audio.onvolumechange = function() {
        volumeBar.value = audio.volume * 100;
    };

    // 音频加载失败时弹窗提示
    audio.onerror = function() {
        alert('无法播放音乐，请检查文件路径或文件格式是否正确。');
    };

    // 拖动进度条调整音频播放位置
    progressBar.oninput = function() {
        if (!isNaN(audio.duration) && isFinite(audio.duration) && audio.duration !== 0) {
            var seekTime = (progressBar.value * audio.duration) / 100;
            audio.currentTime = seekTime;
        }
    };

    // 拖动音量调节条调整音量
    volumeBar.oninput = function() {
        audio.volume = volumeBar.value / 100;
    };

    // 点击音乐列表中的音乐开始播放
    musicList.on('click', function() {
        var musicSrc = $(this).data('src');
        if (musicSrc) {
            audio.pause();
            isPlaying = false;
            $('#playPauseButton').removeClass("icon-zanting");
            $('#playPauseButton').addClass("icon-bofang");

            console.log('选择了音乐：' + musicSrc);

            audio.src = musicSrc;
            if (!isNaN(audio.duration) && isFinite(audio.duration) && audio.duration !== 0) {
                audio.currentTime = (progressBar.value * audio.duration) / 100; // 设置音频播放位置
            }
            audio.play();
            isPlaying = true;
            $('#playPauseButton').removeClass("icon-bofang");
            $('#playPauseButton').addClass("icon-zanting");

            clearSelection(); // 清除之前的选择

            $(this).addClass('active'); // 将当前项设置为选中状态
            $('#musicInfo').text($(this).text()); // 更新音乐信息显示
        } else {
            alert("获取数据失败！");
        }
    });

    // 上一首按钮点击事件
    $('#prevButton').on('click', function() {
        var prevMusic = $('#musicList ul li.active').prev();
        if (prevMusic.length > 0) { // 检查是否存在上一首音乐
            var musicSrc = prevMusic.data('src');
            console.log('选择了上一首音乐：' + musicSrc);

            audio.pause();
            isPlaying = false;
            $('#playPauseButton').removeClass("icon-zanting");
            $('#playPauseButton').addClass("icon-bofang");

            audio.src = musicSrc;
            if (!isNaN(audio.duration) && isFinite(audio.duration) && audio.duration !== 0) {
                audio.currentTime = (progressBar.value * audio.duration) / 100; // 设置音频播放位置
            }
            audio.play();
            isPlaying = true;
            $('#playPauseButton').removeClass("icon-bofang");
            $('#playPauseButton').addClass("icon-zanting");

            clearSelection(); // 清除之前的选择

            prevMusic.addClass('active'); // 将当前项设置为选中状态
            $('#musicInfo').text(prevMusic.text()); // 更新音乐信息显示
        } else {
            console.log('已经是列表中的第一首音乐');
        }
    });

    // 下一首按钮点击事件
    $('#nextButton').on('click', function() {
        var nextMusic = $('#musicList ul li.active').next();
        if (nextMusic.length > 0) { // 检查是否存在下一首音乐
            var musicSrc = nextMusic.data('src');
            console.log('选择了下一首音乐：' + musicSrc);

            audio.pause();
            isPlaying = false;
            $('#playPauseButton').removeClass("icon-zanting");
            $('#playPauseButton').addClass("icon-bofang");

            audio.src = musicSrc;
            if (!isNaN(audio.duration) && isFinite(audio.duration) && audio.duration !== 0) {
                audio.currentTime = (progressBar.value * audio.duration) / 100; // 设置音频播放位置
            }
            audio.play();
            isPlaying = true;
            $('#playPauseButton').removeClass("icon-bofang");
            $('#playPauseButton').addClass("icon-zanting");

            clearSelection(); // 清除之前的选择

            nextMusic.addClass('active'); // 将当前项设置为选中状态
            $('#musicInfo').text(nextMusic.text()); // 更新音乐信息显示
        } else {
            console.log('已经是列表中的最后一首音乐');
        }
    });

    // 显示音量调节条
    $('#volumeBar').on('mouseenter', function() {
        $('#volumeBar').css('transform', 'scaleY(1)');
    });

    // 隐藏音量调节条
    $('#volumeBar').on('mouseleave', function() {
        $('#volumeBar').css('transform', 'scaleY(0)');
    });
});
