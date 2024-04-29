// 定义一个异步函数来使用Plus API读取配置数据
async function readConfigDataWithPlusAPI() {
    return new Promise((resolve, reject) => {
        document.addEventListener('plusready', function() {
            const filePath = 'config/config.json';
            plus.io.resolveLocalFileSystemURL(filePath, function(entry) {
                entry.file(function(file) {
                    const reader = new plus.io.FileReader();
                    reader.onloadend = function(e) {
                        try {
                            const configData = JSON.parse(this.result);
                            resolve(configData);
                        } catch (parseError) {
                            reject(new Error('解析配置文件为JSON时出错: ' + parseError));
                        }
                    };
                    reader.onerror = function(e) {
                        reject(new Error('读取文件内容出错'));
                    };
                    reader.readAsText(file);
                }, function(e) {
                    reject(new Error('打开文件失败: ' + e.message));
                });
            }, function(e) {
                reject(new Error('找不到指定文件: ' + e.message));
            });
        });
    });
}

// 定义一个异步函数来获取音乐列表，使用POST请求
async function fetchMusicList() {
    try {
        const configData = await readConfigDataWithPlusAPI();
        if (!configData) {
            console.error('配置数据不可用');
            return;
        }

        const { origin, user: userName, key } = configData;
        const apiUrl = `${origin}/get_my_music`;

        const requestData = {
            user_name: userName,
            key: key
        };

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('音乐列表获取失败');
        }

        const result = await response.json();
        if (result.code !== 200) {
            throw new Error(`服务器返回错误: ${result.code}`);
        }

        const musicListElement = document.querySelector('#musicList ul');
        musicListElement.innerHTML = ''; 

        const musicList = result.content;
        musicList.forEach((track) => {
            if (track && track.music_name && track.music_url) {
                const listItem = document.createElement('li');
                listItem.textContent = track.music_name;
                listItem.dataset.src = track.music_url;
                if (musicListElement.children.length === 0) {
                    listItem.classList.add('active');
                }
                musicListElement.appendChild(listItem);
            } else {
                console.warn('无效的音乐条目:', track);
            }
        });

    } catch (error) {
        console.error('获取音乐列表时出错:', error);
    }
}

// 当页面加载完毕后初始化音乐列表
document.addEventListener('DOMContentLoaded', fetchMusicList);