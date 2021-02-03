#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

def fingerprint(query):
    query = query.strip().lower()

    query = re.sub(r'\\["\']', '', query)
    query = re.sub(r'[ \n\t\r\f]+', ' ', query)
    query = re.sub(r'\bnull\b', '?', query)
    query = re.sub(r'\b\d+\b', '?', query)

    # "str" => ?
    query = re.sub(r'".*?"', '?', query)
    # 'str' => ?
    query = re.sub(r"'.*?'", '?', query)

    query = re.sub(r'\b(in|values)([\s,]*\([\s?,]*\))+', '\\1(?+)', query)
    query = re.sub(r'\blimit \?(, ?\?| offset \?)?', 'limit ?', query)

    return query

def assertEqual(query, fp):
    q_fp = fingerprint(query)
    if (q_fp != fp):
        print q_fp, " != ", fp

def test_sql_simple():
    assertEqual('SELECT * FROM tbl WHERE col1 = "abc"',
            "select * from tbl where col1 = ?")

    assertEqual(('SELECT * FROM tbl WHERE col1 = 123'),
            "select * from tbl where col1 = ?")

    assertEqual(('SELECT * FROM tbl WHERE id IN ("a", "b", 123)'),
            "select * from tbl where id in(?+)")

    assertEqual(('SELECT * FROM tbl WHERE col1 LIKE "%指纹%"'),
            "select * from tbl where col1 like ?")

    assertEqual(("SELECT col1, created_at FROM tbl\nWHERE col1 like 'abc%'"),
            "select col1, created_at from tbl where col1 like ?")

    assertEqual(('SELECT * FROM tbl WHERE col1 = "abc" LIMIT 10'),
            "select * from tbl where col1 = ? limit ?")

    assertEqual(("CALL MYFUNCTION(123)"),
            "call myfunction(?)")

    assertEqual(("SELECT *, sleep(1) from tbl where pk = 1 or pk = 2 or pk = 3 or pk = 4 or pk = 5 or pk = 6 or pk = 7 or pk = 8 or pk = 9 or pk = 10 or pk = 11"),
            "select *, sleep(?) from tbl where pk = ? or pk = ? or pk = ? or pk = ? or pk = ? or pk = ? or pk = ? or pk = ? or pk = ? or pk = ? or pk = ?")

    assertEqual("UPDATE groups_search SET  charter = '   -------3\\'aaaa\\' XXXXXXXXX.\n    \n    -----------------------------------------------------', show_in_list = 'Y' WHERE group_id='aaaaaaaa'",
            "update groups_search set charter = ?, show_in_list = ? where group_id=?")
    assertEqual("SELECT /*!40001 SQL_NO_CACHE */ * FROM `film`",
                "select /*!? sql_no_cache */ * from `film`")
    assertEqual("select null, '5.001', '5001.' from foo",
            "select ?, ?, ? from foo")
    assertEqual("select 'hello', '\nhello\n', \"hello\", '\\'' from foo",
            "select ?, ?, ?, ? from foo")
    assertEqual("select '\\\\' from foo",
            "select ? from foo")
    assertEqual("select   foo",
            "select foo")
    assertEqual("select 0e0, +6e-30, -6.00 from foo where a = 5.5 or b=0.5 or c=.5",
            "select ?, ?, ? from foo where a = ? or b=? or c=?")

test_sql_simple()
