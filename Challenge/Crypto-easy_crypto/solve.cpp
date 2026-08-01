#include<cstddef>
#include<cctype>
#include<string>
#include<vector>
#include<stdexcept>
#include<iostream>

// x^y
inline unsigned char power(unsigned char x,unsigned char y){
    if(x==0){
        return 0;
    }
    if(y==0){
        return 1;
    }
    unsigned char ret=1;
    for(unsigned char i=0;i<y;++i){
        ret*=x;
    }
    return ret;
};

//将二进制字符串转化为一个unsigned char
inline unsigned char bstr_to_uchar(char const* str,std::size_t size){
    if(str==nullptr){
        throw std::runtime_error("bstr_to_uchar:str!=nullptr");
    }
    if(size==0){
        throw std::runtime_error("bstr_to_uchar:size!=0");
    }
    //x^y
    //size:             4
    //index:0, 1, 2, 3
    //value:1  1  0  1
    //      ^  4-0-1
    unsigned char ret=0;

    for(std::size_t index=0;index<size;++index){
        if(str[index]=='1'){
            ret+=power(2,size-1-index);
        }else if(str[index]=='0'){
            continue;
        }else{
            throw std::runtime_error("bstr_to_uchar:error bchar");
        }
    }
    return ret;
}

inline std::vector<unsigned char> bstr_to_uchar_list(std::string const& str){
    std::vector<unsigned char> ret={};
    std::size_t count=0;
    char const* ptr=nullptr;
    for(std::size_t index=0;index<str.size();++index){
        if(count==0){
            ptr=&str[index];
        }
        if(str[index]=='0'||str[index]=='1'){
            ++count;
        }else if(str[index]==' '){
            ret.emplace_back(bstr_to_uchar(ptr,count));
            count=0;
        }else{
            throw std::runtime_error("bstr_to_uchar_list:error bchar");
        }
    }
    if(count!=0&&ptr!=nullptr){
        ret.emplace_back(bstr_to_uchar(ptr,count));
    }
    return ret;
}

int main(void){
    std::string const bstr="0010 0100 01 110 1111011 11 11111 010 000 0 001101 1010 111 100 0 001101 01111 000 001101 00 10 1 0 010 0 000 1 01111 10 11110 101011 1111101";
    std::vector<unsigned char> ret=bstr_to_uchar_list(bstr);

    std::cout<<"ret: [ ";
    for(auto num:ret){
        std::cout<<static_cast<long long>(num)<<" ";
    }
    std::cout<<"]\n";

    std::cout<<"ret str: ";
    for(unsigned char ch: ret){
        if(!std::isprint(ch)){
            std::cout<<"\\"<<(long long)ch<<' ';
        }else{
            std::cout<<static_cast<char>(ch)<<' ';
        }
    }
    std::cout<<'\n';

    return 0;
}
