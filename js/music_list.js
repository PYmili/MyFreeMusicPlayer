// 定义一个异步函数来读取配置数据
async function readConfigData() {
    try {
        const response = await fetch('config/config.json');
        if (!response.ok) {
            throw new Error('配置文件读取失败');
        }
        return response.json();
    } catch (error) {
        console.error('读取配置数据时出错:', error);
        return null;
    }
}

// 定义一个异步函数来获取音乐列表，使用POST请求
async function fetchMusicList() {
    const configData = await readConfigData();
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

    try {
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
        if (result.code !== 200) { // 假设正常返回的状态码是200，根据实际情况调整
            throw new Error(`服务器返回错误: ${result.code}`);
        }

        const musicList = result.content;

        // 清空现有列表并填充新数据
        const musicListElement = document.querySelector('#musicList ul');
        musicListElement.innerHTML = ''; // 清空现有列表项

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