#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <set>
#include <algorithm>
using std::string;
using std::vector;
using std::set;
typedef string bytes;

const char SP_TEX = char(1);
const char SP_NUL = char(2);
const char SP_END = char(3);
const char header[] = "ItreeFile";
const char version[] = "000001";

class INode {
public:
    string name;
    string text;
	vector<INode> child;

    INode(const string &_name="", const string &_text="") :
		name(_name), text(_text) {
		child.clear();
	}
	INode(const char *_name, const long long &len1, const char *_text, const long long &len2) {
		name.assign(_name, len1);
		text.assign(_text, len2);
		child.clear();
	}

    void add(const INode &);
	int len() const;
	INode & at(const int &);
};

class IRes {
public:
	set<string> name;
	int count;
	string text;

	IRes() { count=0; };
	IRes(const char *_name, const long long &len1, const char *_text, const long long &len2) {
		getName(_name, len1);
		text.assign(_text, len2);
		count=0;
	}
	string makeName() const;
	void getName(const char *, const long long &);
	bool open(const string &);
	bool write(const string &) const;
	bytes toBytes() const;
	static IRes * fromBytes(const char *, int);
};

class IResNodeInfo {
public:
	string name;
	bool isFile;
	IResNodeInfo() {}
	IResNodeInfo(string _name, bool _isFile) : name(_name), isFile(_isFile) {}
	bool operator < (const IResNodeInfo &x) const {
		return isFile==x.isFile?name<x.name:!isFile;
	}
};

class IResNode {
private:
	IResNode *_parent;
	IRes *_data;
	vector<IResNode*> _child;

	void _files(set<IRes*> &, const string &) const;

public:
	string name;

	IResNode() : _parent(NULL), _data(NULL) {}
	~IResNode();

	bool isFile() const;
	bool isRoot() const;
	bool isLoop(IResNode *) const;
	bool hasNode(const string &);
	string currentPath() const;
	int findName(const string &) const;
	void insert(string);
	bool insert(string, const string &);
	void insert(string, IRes *);
	void insert(IResNode *);
	void remove(const int &);
	IResNode * pop(const int &);
	IResNode * copy() const;
	IResNode & parent() const;
	IResNode * parentPointer() const;
	IRes & data() const;
	IRes * dataPointer() const;
	IResNode & getNode(const string &);
	IResNode * getNodePointer(const string &);
	IResNode & at(const int &) const;
	IResNode * atPointer(const int &) const;
	std::vector<string> children(bool isSort=true) const;
	std::vector<IResNodeInfo> childrenInfo(bool isSort=true) const;
	vector<IRes*> files() const;

	static bool isNameVaild(const string &);
};

class ITreeFile {
public:
	string name;

    ITreeFile(const string &_name="") : name(_name) {}
	void getText(INode &, char *&) const;
	void makeText(const INode &, string &) const;
	void makeText(const IResNode &, string &, int &) const;
	void addRes(IResNode &, IRes *) const;
	bool open(INode &, IResNode &) const;
	bool write(const INode &, const IResNode &) const;
};
