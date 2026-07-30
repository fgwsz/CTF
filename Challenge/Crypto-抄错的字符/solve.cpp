#include<cstddef>
#include<array>
#include<unordered_map>
#include<vector>

#include <string>
#include <iostream>
#include <algorithm>
#include <cctype>

std::array<char,19> const str={
    'Q','W','I','H','B','L','G','Z','Z','X',
    'J','S','X','Z','N','V','B','Z','W'
};

std::unordered_map<char,std::vector<char>> const map={
    {'Q',{'Q','q','4','9','0'}},
    {'W',{'W','w'}},
    {'I',{'I','i','1'}},
    {'H',{'H','h'}},
    {'B',{'B','b','6'}},
    {'L',{'L','l','1'}},
    {'G',{'G','g','6','9'}},
    {'Z',{'Z','z','2'}},
    {'X',{'X','x'}},
    {'J',{'J','j'}},
    {'S',{'S','s','5'}},
    {'N',{'N','n'}},
    {'V',{'V','v'}}
};

std::vector<std::array<char,19>> result={};

inline void get_result(std::size_t index){
    //get_result()递归调用栈
    //index:0->1->2->....->18->19
    //                         ^ 跳出
    //
    if(index>18){
        return;
    }
    if(index==0){
        ::result.clear();
        //预先计算总容量提前分配
        std::size_t capacity=1;
        for(auto ch: ::str){
            capacity*=::map.at(ch).size();
        }
        ::result.reserve(capacity);
        //初始化
        ::result.emplace_back(std::array<char,19>{});
    }
    std::size_t i=0;
    auto const& match_list=::map.at(::str[index]);
    //::map每个element都有至少2个char
    //提前复制::result作为备份
    //0...index-1 index
    //[...|       |0|0...]\
    //[...|       |0|0...] >size=old_result.size()
    //[...|       |0|0...]/
    std::vector<std::array<char,19>> tmp=::result;
    for(auto ch : match_list){
        if(i==0){
            //    index
            //[...|ch|0...]\
            //[...|ch|0...] >size=old_result.size()
            //[...|ch|0...]/
            for(auto& arr: result){
                arr[index]=ch;
            }
        }else{
            //    index
            //[...|ch|0...]\
            //[...|ch|0...] >size=old_result.size()
            //[...|ch|0...]/
            for(auto& arr: tmp){
                arr[index]=ch;
            }
            ::result.insert(::result.cend(),tmp.cbegin(),tmp.cend());
        }
        ++i;
    }
    ::get_result(index+1);
}

inline std::vector<std::array<char,19>>& get_result(void){
    ::get_result(0);
    return ::result;
}

// ---------- Base64 解码 ----------
inline std::vector<unsigned char> base64_decode(std::string const& s) {
    static std::string const b64_chars = 
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    auto idx = [&](char c) -> int {
        if (c >= 'A' && c <= 'Z') return c - 'A';
        if (c >= 'a' && c <= 'z') return c - 'a' + 26;
        if (c >= '0' && c <= '9') return c - '0' + 52;
        if (c == '+') return 62;
        if (c == '/') return 63;
        return -1;
    };
    std::vector<unsigned char> res;
    int n = s.size();
    if (n % 4 != 0) return res;
    for (int i = 0; i < n; i += 4) {
        int a[4];
        for (int j = 0; j < 4; ++j) {
            char c = s[i + j];
            if (c == '=') a[j] = 0;
            else {
                int v = idx(c);
                if (v == -1) return std::vector<unsigned char>();
                a[j] = v;
            }
        }
        res.push_back((a[0] << 2) | (a[1] >> 4));
        if (s[i + 2] != '=') res.push_back(((a[1] & 0x0F) << 4) | (a[2] >> 2));
        if (s[i + 3] != '=') res.push_back(((a[2] & 0x03) << 6) | a[3]);
    }
    return res;
}

// ---------- 可读性检测 ----------
bool is_readable(const std::vector<unsigned char>& data) {
    if (data.empty()) return false;
    std::string s(data.begin(), data.end());
    std::transform(s.begin(), s.end(), s.begin(), ::tolower);
    if (s.find("flag{") != std::string::npos
        || s.find("ctf{") != std::string::npos)
        return true;
    for (unsigned char c : data)
        if (c < 32 || c > 126) return false;
    return true;
}

// ---------- 主程序 ----------
int main() {
    auto& combos = get_result();   // 生成所有组合
    std::cout << "总组合数: " << combos.size() << '\n';

    long long count = 0;
    for (const auto& arr : combos) {
        ++count;
        if (count % 500000 == 0)
            std::cout << "已处理 " << count << " 个..." << '\n';

        std::string cand(arr.begin(), arr.end());   // 长度固定为 19
        for (int pad = 0; pad <= 3; ++pad) {
            std::string test = cand + std::string(pad, '=');
            auto raw = base64_decode(test);
            if (raw.empty()) continue;

            if (is_readable(raw)) {
                std::string text(raw.begin(), raw.end());
                std::cout << "[+] 可读: " << test << " -> " << text << '\n';
                if (text.find("flag{") != std::string::npos 
                    || text.find("ctf{") != std::string::npos) {
                    std::cout << "[!!!] 命中 flag!" << '\n';
                    return 0;
                }
            }
        }
    }

    std::cout << "未找到 flag." << '\n';
    return 0;
}
