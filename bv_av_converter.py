class BvAvConverter:
    TABLE = 'FcwAPNKTMug3GV5Lj7EJnHpWsx4tb8haYeviqBz6rkCy12mUSDQX9RdoZf'
    TR = {c: i for i, c in enumerate(TABLE)}
    MAX_AVID = 1 << 51
    BASE = 58
    BVID_LEN = 12
    XOR = 23442827791579
    MASK = 2251799813685247

    @classmethod
    def bv_to_av(cls, bvid: str) -> str:
        """
        BV号转AV号
        :param bvid: BV号 (如: BV17x411w7KC)
        :return: AV号 (如: av170001)
        """
        if not bvid or not isinstance(bvid, str):
            raise ValueError('Invalid BV ID')
        
        # 移除可能的前缀并验证格式
        clean_bvid = bvid
        if clean_bvid.lower().startswith('bv'):
            clean_bvid = clean_bvid[2:]
            
        if len(clean_bvid) != 10:
            # 有时候传入的是带BV的完整ID，长度为12，或者只传后面的10位
            # 上面已经移除了bv前缀，如果原始就是10位不带bv的也能处理
            # 这里检查的是移除前缀后的长度
             raise ValueError('Invalid BV ID format')

        # 构建完整BV号字符数组，用于交换位置
        # 注意：源TS代码逻辑是先把输入变成 'BV' + cleanBvid，然后操作这个字符串
        # 它是基于索引操作的：3, 9 和 4, 7
        # 字符串 "BV17x411w7KC" 索引：
        # 012345678901
        # B V 1 7 x 4 1 1 w 7 K C
        
        chars = list('BV' + clean_bvid)
        
        # 交换字符位置
        chars[3], chars[9] = chars[9], chars[3]
        chars[4], chars[7] = chars[7], chars[4]
        
        # 计算av号
        # 从索引3开始遍历
        temp = 0
        for char in chars[3:]:
            if char not in cls.TR:
                raise ValueError('Invalid character in BV ID')
            temp = temp * cls.BASE + cls.TR[char]
            
        avid = (temp & cls.MASK) ^ cls.XOR
        return f"av{avid}"

    @classmethod
    def av_to_bv(cls, avid: str) -> str:
        """
        AV号转BV号
        :param avid: AV号 (如: av170001)
        :return: BV号 (如: BV17x411w7KC)
        """
        if isinstance(avid, str):
            clean_avid = avid.lower().replace('av', '')
        else:
            clean_avid = str(avid)
            
        try:
            avid_int = int(clean_avid)
        except ValueError:
            raise ValueError('Invalid AV ID')
            
        if avid_int <= 0 or avid_int >= cls.MAX_AVID:
             raise ValueError('AV ID out of range')

        # 准备结果数组，预填充 'BV1' 和空位
        # TS: ['B', 'V', '1', '', '', '', '', '', '', '', '', '']
        result = list('BV1' + ' ' * 9)
        
        # 算法逻辑
        # TS: let temp = (MAX_AVID | avidBigInt) ^ XOR;
        # 这里 MAX_AVID | avidBigInt 实际上可能是为了设置高位或者某种混淆？
        # 等等，源TS代码： let temp = (MAX_AVID | avidBigInt) ^ XOR;
        # 在 avToBv 中使用。
        # 让我们仔细检查 TS 代码逻辑
        # const MAX_AVID = 1n << 51n;
        # (MAX_AVID | avidBigInt) ^ XOR
        
        temp = (cls.MAX_AVID | avid_int) ^ cls.XOR
        
        # 填充字符
        # TS: let idx = BVID_LEN - 1n; // 11
        # while (temp !== 0n) {
        #     result[Number(idx)] = TABLE[Number(temp % BASE)];
        #     temp /= BASE;
        #     idx -= 1n;
        # }
        
        idx = cls.BVID_LEN - 1
        while temp > 0:
            result[idx] = cls.TABLE[temp % cls.BASE]
            temp //= cls.BASE
            idx -= 1
            
        # 交换字符位置
        result[3], result[9] = result[9], result[3]
        result[4], result[7] = result[7], result[4]
        
        return ''.join(result)

def normalize_video_id(video_id: str) -> str:
    """
    标准化视频ID为AV号格式，用于去重比较
    :param video_id: 视频ID (BV号或AV号)
    :return: 标准化的AV号
    """
    if not video_id or not isinstance(video_id, str):
        return video_id
    
    try:
        # 如果是BV号，转换为AV号
        if video_id.lower().startswith('bv'):
            return BvAvConverter.bv_to_av(video_id)
        
        # 如果是AV号，确保格式统一
        if video_id.lower().startswith('av'):
            # 提取纯数字部分
            # 如果是 av123 -> av123
            # 主要是处理大小写
            return video_id.lower()
        
        # 如果是纯数字，当作AV号处理
        if video_id.isdigit():
            return f"av{video_id}"
            
        return video_id
    except Exception:
        # 转换失败时返回原值
        return video_id
