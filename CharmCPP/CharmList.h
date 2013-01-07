#ifndef CHARMLIST_H
#define CHARMLIST_H

#include <map>
#include <string>
#include <fstream>
#include "CryptoLib.h"
#include "CharmListStr.h"
#include "CharmListZR.h"
#include "CharmListG1.h"
#include "CharmListG2.h"
#include "CharmListGT.h"

/* forward declare Element class */
class Element;

class CharmList
{
public:
	CharmList(void); // static list
	~CharmList();
    CharmList(const CharmList&); // copy constructor
	// consider adding remove
	void append(const char *);
	void append(string);
	void append(ZR&);
	void append(const ZR&);
	void append(G1&);
	void append(const G1&);
#if ASYMMETRIC == 1
	void append(G2&);
	void append(const G2&);
	void insert(int, G2&);
	void insert(int, const G2&);
	void insert(int, CharmListG2);
#endif
	void append(GT&);
	void append(const GT&);
	void append(Element&);
	void append(const Element&);
	void append(const CharmList&);

	void insert(int, const char *);
	void insert(int, string);
	void insert(int, ZR&);
	void insert(int, const ZR&);
	void insert(int, CharmListZR);
	void insert(int, G1&);
	void insert(int, const G1&);
	void insert(int, CharmListG1);
	void insert(int, GT&);
	void insert(int, const GT&);
	void insert(int, CharmListGT);
	void insert(int, Element&);
	void insert(int, const Element&);
	//void append(const CharmList&);

	int length(); // return length of lists
	string printAtIndex(int index);

	// retrieve a particular index
	CharmList operator+(const Element&) const;
	CharmList operator+(const CharmList&) const;
	Element& operator[](const int index);
	CharmList& operator=(const CharmList&);
	//Element& operator=(const GT&);
    friend ostream& operator<<(ostream&, const CharmList&);
private:
	int cur_index;
	map<int, Element> list;
};

class Element
{
public:
	// public values for now
	int type;
	ZR zr;
	G1 g1;
	GT gt;
	CharmListZR zrList;
	CharmListG1 g1List;
	CharmListGT gtList;
	string strPtr;
	Element();
	~Element();
	Element(const char *);
	Element(string);
	Element(ZR&);
	Element(CharmListZR&);
	Element(G1&);
	Element(CharmListG1&);
#if ASYMMETRIC == 1
	G2 g2;
	CharmListG2 g2List;
	Element(G2&);
	Element(CharmListG2&);
 	G2 getG2(); // returns value (or copy)
 	CharmListG2 getListG2(); // returns value (or copy)
 	G2& getRefG2(); // returns reference for G2 (for cleanup)
#endif
	Element(GT&);
	Element(CharmListGT&);
	Element(CharmList&);
 	Element(const Element& e);
 	ZR getZR(); // returns value (or copy)
 	ZR& getRefZR(); // returns reference for ZR (for cleanup)
 	CharmListZR getListZR(); // returns value (or copy)
 	G1 getG1(); // getter methods
 	CharmListG1 getListG1(); // returns value (or copy)
 	G1& getRefG1(); // getter methods
 	GT getGT();
 	CharmListGT getListGT(); // returns value (or copy)
 	GT& getRefGT();
	string str();

	friend void deserialize(Element&, string);
	friend string serialize(Element&);

	CharmList operator+(const Element&) const;       // operator+()
	CharmList operator+(const CharmList&) const;
 	Element operator=(const Element& e);

    friend ostream& operator<<(ostream&, const Element&);
};

/* base-64 encoding functions */
string _base64_encode(unsigned char const* bytes_to_encode, unsigned int in_len);
string _base64_decode(string const& encoded_string);
bool is_base64(unsigned char c);

extern string Element_ToBytes(Element &e);
extern int Element_FromBytes(Element &e, int type, unsigned char *data);

#endif