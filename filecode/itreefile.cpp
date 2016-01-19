#include "itreefile.h"

/* getfile */
#include <sys/stat.h>
#define R(x) if(x!=1) return false
long long getFileSize(const char *path) {
	struct stat statbuff;
	if(stat(path, &statbuff) >= 0)
		return statbuff.st_size;
	return 0;
}
bool readFile(const string &name, string &text) {
	FILE *fio=fopen(name.c_str(), "rb");
	if(fio==NULL) {
		return false;
	}
	long long len=getFileSize(name.c_str());
	char *buf=new char[len+1];
	R(fread(buf, len, 1, fio));
	text.assign(buf, len);
	delete[] buf;
	fclose(fio);
	return true;
}
bool writeFile(const string &name, const string &text, const string &cmd="wb") {
	FILE *fio=fopen(name.c_str(), cmd.c_str());
	if(fio==NULL) {
		return false;
	}
	R(fwrite(text.c_str(), text.size(), 1, fio));
	fclose(fio);
	return true;
}
bool moveFile(const string &from, const string &to) {
	return rename(from.c_str(), to.c_str())==0;
}
bool isExist(const string &name) {
	FILE *fio=fopen(name.c_str(), "rb");
	bool ret=fio!=NULL;
	if(fio!=NULL) {
		fclose(fio);
	}
	return ret;
}

/* INode */
void INode::add(const INode &x) {
	child.push_back(x);
}
int INode::len() const {
	return child.size();
}
INode & INode::at(const int &x) {
	return child[x];
}

/* IRes */
bool IRes::open(const string &filename) {
	return readFile(filename, text);
}
bool IRes::write(const string &filename) const {
	return writeFile(filename, text);
}
string IRes::makeName() const {
	string ret;
	for(set<string>::iterator it=name.begin(); it!=name.end(); ++it) {
		ret.append(*it);
		ret.push_back(SP_TEX);
	}
	return ret;
}
void IRes::getName(const char *_name, const long long &len) {
	for(long long i=0, j=0; i<len; ++i) {
		if(_name[i]==SP_TEX) {
			if(i-j) {
				name.insert(string(_name+j, i-j));
			}
			j=i+1;
		}
	}
}
bytes IRes::toBytes() const {
	return text;
}
IRes * IRes::fromBytes(const char *s, int len) {
	IRes *x=new IRes();
	x->count=1;
	x->text.assign(s, len);
	return x;
}

/* IResNode */
IResNode::~IResNode() {
	if(_data!=NULL) {
		_data->count--;
		if(_data->count==0) {
			delete _data;
		}
	}
	for(vector<IResNode *>::iterator it=_child.begin(); it!=_child.end(); ++it) {
		delete *it;
	}
}
bool IResNode::isFile() const {
	return _data!=NULL;
}
bool IResNode::isRoot() const {
	return _parent==NULL;
}
bool IResNode::isLoop(IResNode *y) const {
	for(const IResNode *x=this; x; x=x->_parent) {
		if(x==y) {
			return true;
		}
	}
	return false;
}
bool IResNode::hasNode(const string &path) {
	IResNode *node=getNodePointer(path);
	return node!=NULL;
}
string IResNode::currentPath() const {
	if(_parent==NULL) {
		return "";
	}
	return _parent->currentPath()+_parent->name+"/";
}
int IResNode::findName(const string &str) const {
	for(std::size_t i=0; i<_child.size(); ++i) {
		if(_child[i]->name==str) {
			return (int)i;
		}
	}
	return -1;
}
void IResNode::insert(string _path) {
	std::size_t pos=_path.find('/');
	string _name;

	if(pos!=string::npos) {
		_name.assign(_path.begin(), _path.begin()+pos);
		_path.assign(_path.begin()+pos+1, _path.end());
	}
	else {
		_name=_path;
		_path="";
	}
	
	int row=findName(_name);
	IResNode *x;

	if(row==-1) {
		x=new IResNode();
		x->_parent=this;
		x->name=_name;
		_child.push_back(x);
	}
	else {
		x=_child[row];
	}

	if(_path!="") {
		x->insert(_path);
	}
}
bool IResNode::insert(string _path, const string &file) {
	std::size_t pos=_path.find('/');
	string _name;

	if(pos!=string::npos) {
		_name.assign(_path.begin(), _path.begin()+pos);
		_path.assign(_path.begin()+pos+1, _path.end());
	}
	else {
		_name=_path;
		_path="";
	}
	
	int row=findName(_name);
	IResNode *x;

	if(row==-1) {
		x=new IResNode();
		x->_parent=this;
		x->name=_name;
		_child.push_back(x);
	}
	else {
		x=_child[row];
	}

	if(_path!="") {
		return x->insert(_path, file);
	}
	else {
		IRes *res=new IRes;
		if(!res->open(file)) {
			_child.pop_back();
			return false;
		}
		res->count++;

		x->_data=res;
		return true;
	}
}
void IResNode::insert(string _path, IRes *res) {
	std::size_t pos=_path.find('/');
	string _name;

	if(pos!=string::npos) {
		_name.assign(_path.begin(), _path.begin()+pos);
		_path.assign(_path.begin()+pos+1, _path.end());
	}
	else {
		_name=_path;
		_path="";
	}
	
	int row=findName(_name);
	IResNode *x;

	if(row==-1) {
		x=new IResNode();
		x->_parent=this;
		x->name=_name;
		_child.push_back(x);
	}
	else {
		x=_child[row];
	}

	if(_path!="") {
		x->insert(_path, res);
	}
	else {
		res->count++;

		x->_data=res;
	}
}
void IResNode::insert(IResNode *x) {
	_child.push_back(x);
	x->_parent=this;
}
void IResNode::remove(const int &pos) {
	IResNode *x = *(_child.begin()+pos);
	_child.erase(_child.begin()+pos);
	delete x;
}
IResNode * IResNode::pop(const int &pos) {
	IResNode *x = *(_child.begin()+pos);
	_child.erase(_child.begin()+pos);
	return x;
}
IResNode * IResNode::copy() const {
	IResNode *x=new IResNode();
	x->_data=_data;
	x->name=name;
	if(x->_data!=NULL) {
		x->_data->count++;
	}
	for(std::size_t i=0; i<_child.size(); ++i) {
		IResNode *y=_child[i]->copy();
		y->_parent=x;
		x->_child.push_back(y);
	}
	return x;
}
IResNode & IResNode::parent() const {
	return *_parent;
}
IResNode * IResNode::parentPointer() const {
	return _parent;
}
IRes & IResNode::data() const {
	return *_data;
}
IRes * IResNode::dataPointer() const {
	return _data;
}
IResNode & IResNode::getNode(const string &path) {
	return *getNodePointer(path);
}
IResNode * IResNode::getNodePointer(const string &path) {
	if(path.size()==0) {
		return NULL;
	}
	string name="";
	IResNode *now=this;
	size_t begin=0,
		   end=path.size();
	if(path[0]=='/') {
		begin+=1;
	}
	if(path[end-1]=='/') {
		end-=1;
	}
	if(begin>=end) {
		return NULL;
	}
	for(size_t i=begin; i<end; ++i) {
		if(path[i]=='/') {
			int pos=now->findName(name);
			if(pos==-1) {
				return NULL;
			}
			now=now->atPointer(pos);
			name="";
		}
		else {
			name.push_back(path[i]);
		}
	}
	int pos=now->findName(name);
	if(pos==-1) {
		return NULL;
	}
	return now->atPointer(pos);
}
IResNode & IResNode::at(const int &index) const {
	return *_child[index];
}
IResNode * IResNode::atPointer(const int &index) const {
	return _child[index];
}
vector<string> IResNode::children(bool isSort) const {
	vector<string> list;
	for(std::size_t i=0; i<_child.size(); ++i) {
		list.push_back(_child[i]->name);
	}
	if(isSort) {
		sort(list.begin(), list.end());
	}
	return list;
}
vector<IResNodeInfo> IResNode::childrenInfo(bool isSort) const {
	vector<IResNodeInfo> list;
	for(std::size_t i=0; i<_child.size(); ++i) {
		list.push_back(IResNodeInfo(_child[i]->name, _child[i]->isFile()));
	}
	if(isSort) {
		sort(list.begin(), list.end());
	}
	return list;
}
void IResNode::_files(set<IRes*> &s, const string &path) const {
	if(_data!=NULL) {
		if(s.find(_data)==s.end()) {
			_data->name.clear();
			s.insert(_data);
		}
		_data->name.insert(path+name);
	}
	for(std::size_t i=0; i<_child.size(); ++i) {
		_child[i]->_files(s, path+name+"/");
	}
}
vector<IRes*> IResNode::files() const {
	set<IRes*> s;
	_files(s, "");
	return vector<IRes*> (s.begin(), s.end());
}
bool IResNode::isNameVaild(const string &str) {
	if(str.find('/')!=string::npos) {
		return false;
	}
	return true;
}

/* ITreeFile */
void ITreeFile::getText(INode &root, char *&str) const {
	for(; *str!=SP_END; ) {
		INode x;
		for(; *str!=SP_TEX; x.name.push_back(*str), ++str);
		++str;
		for(; *str!=SP_TEX; x.text.push_back(*str), ++str);
		++str;
		if(*str!=SP_NUL) {
			getText(x, str);
		}
		else {
			++str;
		}
		root.child.push_back(x);
	}
	++str;
}
void ITreeFile::makeText(const INode &x, string &s) const {
	for(std::size_t i=0; i<x.child.size(); ++i) {
		s.append(x.child[i].name);
		s.push_back(SP_TEX);
		s.append(x.child[i].text);
		s.push_back(SP_TEX);
		if(x.child[i].child.size()) {
			makeText(x.child[i], s);
		}
		else {
			s.push_back(SP_NUL);
		}
	}
	if(x.child.size()) {
		s.push_back(SP_END);
	}
}
void ITreeFile::makeText(const IResNode &x, string &s, int &cnt) const {
	s="";
	vector<IRes*> list=x.files();
	for(vector<IRes*>::iterator it=list.begin(); it!=list.end(); ++it) {
		long long len=0;
		
		string name=(*it)->makeName();
		len=name.size();
		s.append((char *)&len, 8);
		s.append(name);

		len=(*it)->text.size();
		s.append((char *)&len, 8);
		s.append((*it)->text);
	}
	cnt=list.size();
}
void ITreeFile::addRes(IResNode &x, IRes *res) const {
	for(set<string>::iterator it=res->name.begin(); it!=res->name.end(); ++it) {
		x.insert(string(it->begin()+1, it->end()), res);
	}
}
bool ITreeFile::open(INode &node_root, IResNode &res_root) const {
	long long len=0, len1=0, len2=0;
	FILE *fio=fopen(name.c_str(), "rb");
	if(fio==NULL) {
		return false;
	}

	/* 文件大小用8字节来存储
	   资源个数用4字节来存储 */

	/* 获取版本信息 */
	len=strlen(header);
	char *str=new char[len+1];
	R(fread(str, len, 1, fio));
	str[len] = '\0';
	if(strcmp(str, header)!=0) {
		return false;
	}
	delete[] str;

	len=strlen(version);
	str=new char[len+1];
	R(fread(str, len, 1, fio));
	str[len] = '\0';
	if(strcmp(str, version)!=0) {
		return false;
	}
	delete[] str;
	
	/* 获取主内容 */
	R(fread(&len, 8, 1, fio));
	char *buf=new char[len+1], *bg=buf;
	if(len>0) {
		R(fread(buf, len, 1, fio));
	}
	if(*bg) {
		node_root.child.clear();
		getText(node_root, bg);
	}
	delete[] buf;

	/* 获取资源 */
	int cnt=0;
	R(fread(&cnt, 4, 1, fio));
	for(; cnt--; ) {
		len1=0;
		R(fread(&len1, 8, 1, fio));
		char *name=new char[len1+1];
		R(fread(name, len1, 1, fio));

		len2=0;
		R(fread(&len2, 8, 1, fio));
		char *text=new char[len2+1];
		R(fread(text, len2, 1, fio));

		addRes(res_root, new IRes(name, len1, text, len2));

		delete[] name;
		delete[] text;
	}

	fclose(fio);
	return true;
}
bool ITreeFile::write(const INode &node_root, const IResNode &res_root) const {
	int cnt=0;
	string text, res, writeName=name+"~";
	for(; isExist(writeName); writeName+="~");

	makeText(node_root, text);
	makeText(res_root, res, cnt);
	FILE *fio=fopen(writeName.c_str(), "wb");
	if(fio==NULL) {
		return false;
	}
	R(fwrite(header, strlen(header), 1, fio));
	R(fwrite(version, strlen(version), 1, fio));
	
	long long len=text.size();
	R(fwrite(&len, 8, 1, fio));
	if(text.size()>0) {
		R(fwrite(text.c_str(), text.size(), 1, fio));
	}
	R(fwrite(&cnt, 4, 1, fio));
	if(res.size()>0) {
		R(fwrite(res.c_str(), res.size(), 1, fio));
	}

	fclose(fio);
	bool ret=moveFile(writeName, name);
	if(!ret) {
		remove(writeName.c_str());
	}
	return ret;
}
#undef R
/* test */

/*
void outpic(string name, IRes &x) {
	FILE *fio=fopen(name.c_str(), "wb");
	fwrite(x.text.c_str(), x.text.size(), 1, fio);
	fclose(fio);
}
void debug(INode &x, string tab="") {
	for(vector<INode>::iterator it=x.child.begin(); it!=x.child.end(); ++it) {
		printf("%s[%s, %s]\n", tab.c_str(), it->name.c_str(), it->text.c_str());
		debug(*it, tab+"  ");
	}
}
void debug(IResNode &x, string tab="") {
	vector<string> c=x.children();
	for(std::size_t i=0; i<c.size(); ++i) {
		printf("%s%s\n", tab.c_str(), c[i].c_str());
		debug(x.at(x.findName(c[i])), tab+"  ");
	}
}
void test() {
	ITreeFile a("a.it");
	INode x;
	IResNode y;
	a.open(x, y);
	x.add(INode("abfbd", "sfsk"));
	x.add(INode("bcdssf", "fjdsiojf"));
	x.child[0].add(INode("cdsjoif", "gsofjdio"));
	x.child[1].add(INode("ejsiofj", "fdsoijfs"));
	x.child[1].add(INode("ddisofj", "eodfijsi"));

	y.insert("dsjfiod/a.jpg", "1.jpg");
	y.insert("dsjfiod/b.jpg", "1.jpg");
	y.insert("dshafoi/sdfjidos/b.jpg", "1.jpg");
	IRes *p=new IRes();
	p->open("1.jpg");
	y.insert("abc/a.jpg", p);
	y.insert("abc/b.jpg", p);
	printf("%d\n", p->count);
	debug(x);
	puts("");
	debug(y);
	a.write(x, y);
}

int main() {
	test();
	return 0;
}
*/
