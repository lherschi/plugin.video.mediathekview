# -*- coding: utf-8 -*-
"""
The local SQlite database module

Copyright 2017-2019, Leo Moll
SPDX-License-Identifier: MIT
"""
# pylint: disable=too-many-lines,line-too-long

import resources.lib.appContext as appContext


class StoreMySQLSetup(object):

    def __init__(self, dbCon):
        self.logger = appContext.MVLOGGER.get_new_logger('StoreMySQLSetup')
        self.settings = appContext.MVSETTINGS
        self.conn = dbCon
        self._setupSchema = 'CREATE DATABASE IF NOT EXISTS `{}` DEFAULT CHARACTER SET utf8mb4;'.format(self.settings.getDatabaseSchema())
        self._setupScript = """
-- ----------------------------
-- DB V2 
DROP PROCEDURE IF EXISTS `ftUpdateStart`;
DROP PROCEDURE IF EXISTS `ftUpdateEnd`;
DROP PROCEDURE IF EXISTS `ftInsertShow`;
DROP PROCEDURE IF EXISTS `ftInsertChannel`;
DROP TABLE IF EXISTS `status`;
DROP TABLE IF EXISTS `show`;
DROP TABLE IF EXISTS `film`;
DROP TABLE IF EXISTS `channel`;
-- ----------------------------
--  Table structure for film
-- ----------------------------
DROP TABLE IF EXISTS film;
CREATE TABLE film (
    idhash         char(32)        NOT NULL,
    dtCreated      INT             NOT NULL,
    touched        smallint(1)     NOT NULL,
    channel        varchar(32)     NOT NULL,
    showid         char(8)         NOT NULL,
    showname       varchar(128)    NOT NULL,
    title          varchar(128)    NOT NULL,
    aired          INT             NOT NULL,
    duration       INT             NOT NULL,
    description    varchar(1024)   NULL,
    url_sub        varchar(2048)    NULL,
    url_video      varchar(2048)    NULL,
    url_video_sd   varchar(2048)    NULL,
    url_video_hd   varchar(2048)    NULL
) ENGINE=InnoDB CHARSET=utf8mb4;
--
CREATE INDEX idx_idhash ON film (idhash);
CREATE INDEX idx_channel ON film (channel);
CREATE INDEX idx_showid ON film (showid);
-- ----------------------------
--  Table structure for status
-- ----------------------------
DROP TABLE IF EXISTS status;
CREATE TABLE status (
    status          varchar(255)    NOT NULL,
    lastupdate      INT             NOT NULL,
    lastFullUpdate  INT             NOT NULL,
    filmupdate      INT             NOT NULL,
    version         INT             NOT NULL
) ENGINE=InnoDB;
-- ----------------
INSERT INTO status values ('UNINIT',0,0,0,3);
--
"""

    def setupDatabase(self):
        self.logger.debug('Start DB setup for schema {}', self.settings.getDatabaseSchema())
        #
        #
        try:
            self.conn.database = self.settings.getDatabaseSchema()
            rs = self.conn.execute("SHOW DATABASES LIKE '{}'".format(self.settings.getDatabaseSchema()))
            if len(rs) > 0:
                self.logger.debug('MySql Schema exists - no action')
            else:
                raise Exception('DB', 'DB')
        except Exception:
            self.logger.debug('MySql Schema does not exists - setup schema')
            cursor = self.conn.getConnection().cursor()
            cursor.execute(self._setupSchema)
            self.logger.debug("MySql Schema '{}':", self._setupSchema)
            cursor.execute("USE {}".format(self.settings.getDatabaseSchema()))
            self.logger.debug("Use '{}':", self.settings.getDatabaseSchema())
            cursor.close()
            self.conn.database = self.settings.getDatabaseSchema()
        #
        con = self.conn.getConnection()
        cursor = con.cursor()
        for result in cursor.execute(self._setupScript, multi=True):
          if result.with_rows:
            self.logger.debug("Rows produced by statement '{}':", result.statement)
            self.logger.debug(result.fetchall())
          else:
            self.logger.debug("Number of rows affected by statement '{}': {}", result.statement, result.rowcount)
        cursor.close()
        con.commit()
        self.logger.debug('End DB setup')
