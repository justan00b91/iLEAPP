# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 1.1
#
#   Description:
#   Parses Assets associated with Non-Shared Albums found in the PhotoData-Photos.sqlite and supports iOS 11-17.
#   Parses limited assets data with full non-shared album data.
#   This parser is based on research and SQLite Queries written by Scott Koenig
#   This is very large query and script, I recommend opening the TSV generated report with Zimmerman's Tools
#   https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search and filter the results.
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph22assetsinnonsharedalbumsphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break

    if report_folder.endswith('/') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("10.3.4"):
        logfunc("Unsupported version for PhotoData-Photos.sqlite assets in Non-Shared Albums from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("11")) & (version.parse(iosversion) < version.parse("12")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',       
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',       
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_20ASSETS z20Assets ON z20Assets.Z_27ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z20Assets.Z_20ALBUMS
            LEFT JOIN Z_19ALBUMLISTS z19AlbumLists ON z19AlbumLists.Z_19ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z19AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55]))

                counter += 1

            description = 'Parses Assets associated with Non-Shared Albums found in the PhotoData-Photos.sqlite' \
                          ' from iOS 11. Parses limited asset data with full non-shared album data.'
            report = ArtifactHtmlReport('Photos.sqlite-E-Asset_In_Albums')
            report.start_artifact_report(report_folder, 'Ph22-Assets in Non-Shared Albums-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-zPK-1',
                            'zAsset-Directory-Path-2',
                            'zAsset-Filename-3',
                            'zAddAssetAttr- Original Filename-4',
                            'zCldMast- Original Filename-5',
                            'zAddAssetAttr- Creator Bundle ID-6',
                            'zAsset-Visibility State-7',
                            'zAsset-Saved Asset Type-8',
                            'zAsset- SortToken -CameraRoll-9',
                            'zAsset-Added Date-10',
                            'zCldMast-Creation Date-11',
                            'zAddAssetAttr-Time Zone Name-12',
                            'zAddAssetAttr-EXIF-String-13',
                            'zAsset-Modification Date-14',
                            'zAsset-Last Shared Date-15',
                            'zAsset-Trashed Date-16',
                            'zAddAssetAttr-zPK-17',
                            'zAsset-UUID = store.cloudphotodb-18',
                            'zAddAssetAttr-Master Fingerprint-19',
                            'zGenAlbum-Start Date-20',
                            'zGenAlbum-End Date-21',
                            'ParentzGenAlbum-UUID-22',
                            'ParentzGenAlbum-Cloud GUID-23',
                            'ParentzGenAlbum- Title-24',
                            'zGenAlbum- Title-User&System Applied-25',
                            'zGenAlbum-UUID-26',
                            'zGenAlbum-Cloud GUID-27',
                            'ParentzGenAlbum-Pending Items Count-28',
                            'ParentzGenAlbum-Pending Items Type-29',
                            'ParentzGenAlbum-Kind-30',
                            'ParentzGenAlbum-Cloud-Local-State-31',
                            'ParentzGenAlbum-Sync Event Order Key-32',
                            'ParentzGenAlbum-Pinned-33',
                            'ParentzGenAlbum-Custom Sort Key-34',
                            'ParentzGenAlbum-Custom Sort Ascending-35',
                            'ParentzGenAlbum-Custom Query Type-36',
                            'ParentzGenAlbum-Trashed State-37',
                            'ParentzGenAlbum-Trash Date-38',
                            'zGenAlbum-Pending Items Count-39',
                            'zGenAlbum-Pending Items Type-40',
                            'zGenAlbum- Cached Photos Count-41',
                            'zGenAlbum- Cached Videos Count-42',
                            'zGenAlbum- Cached Count-43',
                            'zGenAlbum-Has Unseen Content-44',
                            'zGenAlbum-Unseen Asset Count-45',
                            'zGenAlbum-zENT- Entity-46',
                            'zGenAlbum-Album Kind-47',
                            'zGenAlbum-Cloud_Local_State-48',
                            'zGenAlbum-Sync Event Order Key-49',
                            'zGenAlbum-Pinned-50',
                            'zGenAlbum-Custom Sort Key-51',
                            'zGenAlbum-Custom Sort Ascending-52',
                            'zGenAlbum-Custom Query Type-53',
                            'zGenAlbum-Trashed State-54',
                            'zGenAlbum-Trash Date-55')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available from PhotoData-Photos.sqlite for Assets in Non-Shared Albums')

            db.close()
        return

    elif (version.parse(iosversion) >= version.parse("12")) & (version.parse(iosversion) < version.parse("13")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',       
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',       
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_23ASSETS z23Assets ON z23Assets.Z_30ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z23Assets.Z_23ALBUMS
            LEFT JOIN Z_22ALBUMLISTS z22AlbumLists ON z22AlbumLists.Z_22ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z22AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57]))

                counter += 1

            description = 'Parses Assets associated with Non-Shared Albums found in the PhotoData-Photos.sqlite' \
                          ' from iOS 12. Parses limited asset data with full non-shared album data.'
            report = ArtifactHtmlReport('Photos.sqlite-E-Asset_In_Albums')
            report.start_artifact_report(report_folder, 'Ph22-Assets in Non-Shared Albums-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-zPK-1',
                            'zAsset-Directory-Path-2',
                            'zAsset-Filename-3',
                            'zAddAssetAttr- Original Filename-4',
                            'zCldMast- Original Filename-5',
                            'zAddAssetAttr- Creator Bundle ID-6',
                            'zAsset-Visibility State-7',
                            'zAsset-Saved Asset Type-8',
                            'zAsset- SortToken -CameraRoll-9',
                            'zAsset-Added Date-10',
                            'zCldMast-Creation Date-11',
                            'zAddAssetAttr-Time Zone Name-12',
                            'zAddAssetAttr-EXIF-String-13',
                            'zAsset-Modification Date-14',
                            'zAsset-Last Shared Date-15',
                            'zAsset-Trashed Date-16',
                            'zAddAssetAttr-zPK-17',
                            'zAsset-UUID = store.cloudphotodb-18',
                            'zAddAssetAttr-Master Fingerprint-19',
                            'zGenAlbum-Start Date-20',
                            'zGenAlbum-End Date-21',
                            'ParentzGenAlbum-UUID-22',
                            'ParentzGenAlbum-Cloud GUID-23',
                            'ParentzGenAlbum- Title-24',
                            'zGenAlbum- Title-User&System Applied-25',
                            'zGenAlbum-UUID-26',
                            'zGenAlbum-Cloud GUID-27',
                            'ParentzGenAlbum-Pending Items Count-28',
                            'ParentzGenAlbum-Pending Items Type-29',
                            'ParentzGenAlbum-Kind-30',
                            'ParentzGenAlbum-Cloud-Local-State-31',
                            'ParentzGenAlbum-Sync Event Order Key-32',
                            'ParentzGenAlbum-Pinned-33',
                            'ParentzGenAlbum-Custom Sort Key-34',
                            'ParentzGenAlbum-Custom Sort Ascending-35',
                            'ParentzGenAlbum-Custom Query Type-36',
                            'ParentzGenAlbum-Trashed State-37',
                            'ParentzGenAlbum-Trash Date-38',
                            'ParentzGenAlbum-Cloud Delete State-39',
                            'zGenAlbum-Pending Items Count-40',
                            'zGenAlbum-Pending Items Type-41',
                            'zGenAlbum- Cached Photos Count-42',
                            'zGenAlbum- Cached Videos Count-43',
                            'zGenAlbum- Cached Count-44',
                            'zGenAlbum-Has Unseen Content-45',
                            'zGenAlbum-Unseen Asset Count-46',
                            'zGenAlbum-zENT- Entity-47',
                            'zGenAlbum-Album Kind-48',
                            'zGenAlbum-Cloud_Local_State-49',
                            'zGenAlbum-Sync Event Order Key-50',
                            'zGenAlbum-Pinned-51',
                            'zGenAlbum-Custom Sort Key-52',
                            'zGenAlbum-Custom Sort Ascending-53',
                            'zGenAlbum-Custom Query Type-54',
                            'zGenAlbum-Trashed State-55',
                            'zGenAlbum-Trash Date-56',
                            'zGenAlbum-Cloud Delete State-57')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available from PhotoData-Photos.sqlite for Assets in Non-Shared Albums')

            db.close()
        return

    elif (version.parse(iosversion) >= version.parse("13")) & (version.parse(iosversion) < version.parse("14")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',       
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',       
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',       
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZGENERICASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_34ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_3ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60]))

                counter += 1

            description = 'Parses Assets associated with Non-Shared Albums found in the PhotoData-Photos.sqlite' \
                          ' from iOS 13. Parses limited asset data with full non-shared album data.'
            report = ArtifactHtmlReport('Photos.sqlite-E-Asset_In_Albums')
            report.start_artifact_report(report_folder, 'Ph22-Assets in Non-Shared Albums-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-zPK-1',
                            'zAsset-Directory-Path-2',
                            'zAsset-Filename-3',
                            'zAddAssetAttr- Original Filename-4',
                            'zCldMast- Original Filename-5',
                            'zAddAssetAttr- Creator Bundle ID-6',
                            'zAsset-Visibility State-7',
                            'zAsset-Saved Asset Type-8',
                            'zAsset- SortToken -CameraRoll-9',
                            'zAsset-Added Date-10',
                            'zCldMast-Creation Date-11',
                            'zAddAssetAttr-Time Zone Name-12',
                            'zAddAssetAttr-EXIF-String-13',
                            'zAsset-Modification Date-14',
                            'zAsset-Last Shared Date-15',
                            'zAsset-Trashed Date-16',
                            'zAddAssetAttr-zPK-17',
                            'zAsset-UUID = store.cloudphotodb-18',
                            'zAddAssetAttr-Master Fingerprint-19',
                            'zGenAlbum-Creation Date-20',
                            'zGenAlbum-Start Date-21',
                            'zGenAlbum-End Date-22',
                            'ParentzGenAlbum-UUID-23',
                            'ParentzGenAlbum-Cloud GUID-24',
                            'ParentzGenAlbum- Title-25',
                            'zGenAlbum- Title-User&System Applied-26',
                            'zGenAlbum-UUID-27',
                            'zGenAlbum-Cloud GUID-28',
                            'ParentzGenAlbum-Pending Items Count-29',
                            'ParentzGenAlbum-Pending Items Type-30',
                            'ParentzGenAlbum-Kind-31',
                            'ParentzGenAlbum-Cloud-Local-State-32',
                            'ParentzGenAlbum-Sync Event Order Key-33',
                            'ParentzGenAlbum-Pinned-34',
                            'ParentzGenAlbum-Custom Sort Key-35',
                            'ParentzGenAlbum-Custom Sort Ascending-36',
                            'ParentzGenAlbum-Project Document Type-37',
                            'ParentzGenAlbum-Custom Query Type-38',
                            'ParentzGenAlbum-Trashed State-39',
                            'ParentzGenAlbum-Trash Date-40',
                            'ParentzGenAlbum-Cloud Delete State-41',
                            'zGenAlbum-Pending Items Count-42',
                            'zGenAlbum-Pending Items Type-43',
                            'zGenAlbum- Cached Photos Count-44',
                            'zGenAlbum- Cached Videos Count-45',
                            'zGenAlbum- Cached Count-46',
                            'zGenAlbum-Has Unseen Content-47',
                            'zGenAlbum-Unseen Asset Count-48',
                            'zGenAlbum-zENT- Entity-49',
                            'zGenAlbum-Album Kind-50',
                            'zGenAlbum-Cloud_Local_State-51',
                            'zGenAlbum-Sync Event Order Key-52',
                            'zGenAlbum-Pinned-53',
                            'zGenAlbum-Custom Sort Key-54',
                            'zGenAlbum-Custom Sort Ascending-55',
                            'zGenAlbum-Project Document Type-56',
                            'zGenAlbum-Custom Query Type-57',
                            'zGenAlbum-Trashed State-58',
                            'zGenAlbum-Trash Date-59',
                            'zGenAlbum-Cloud Delete State-60')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available from PhotoData-Photos.sqlite for Assets in Non-Shared Albums')

            db.close()
        return

    elif (version.parse(iosversion) >= version.parse("14")) & (version.parse(iosversion) < version.parse("15")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZCREATORBUNDLEID AS 'zAddAssetAttr- Creator Bundle ID',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZCREATORBUNDLEID AS 'zGenAlbum-Creator Bundle Id',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
            WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
        END AS 'ParentzGenAlbum-Is Prototype',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',       
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_26ASSETS z26Assets ON z26Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z26Assets.Z_26ALBUMS
            LEFT JOIN Z_25ALBUMLISTS z25AlbumLists ON z25AlbumLists.Z_25ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z25AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65], row[66]))

                counter += 1

            description = 'Parses Assets associated with Non-Shared Albums found in the PhotoData-Photos.sqlite' \
                          ' from iOS 14. Parses limited asset data with full non-shared album data.'
            report = ArtifactHtmlReport('Photos.sqlite-E-Asset_In_Albums')
            report.start_artifact_report(report_folder, 'Ph22-Assets in Non-Shared Albums-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-zPK-1',
                            'zAsset-Directory-Path-2',
                            'zAsset-Filename-3',
                            'zAddAssetAttr- Original Filename-4',
                            'zCldMast- Original Filename-5',
                            'zAddAssetAttr- Creator Bundle ID-6',
                            'zAddAssetAttr-Imported By Display Name-7',
                            'zAsset-Visibility State-8',
                            'zAsset-Saved Asset Type-9',
                            'zAddAssetAttr-Share Type-10',
                            'zAsset- SortToken -CameraRoll-11',
                            'zAsset-Added Date-12',
                            'zCldMast-Creation Date-13',
                            'zAddAssetAttr-Time Zone Name-14',
                            'zAddAssetAttr-EXIF-String-15',
                            'zAsset-Modification Date-16',
                            'zAsset-Last Shared Date-17',
                            'zAsset-Trashed Date-18',
                            'zAddAssetAttr-zPK-19',
                            'zAsset-UUID = store.cloudphotodb-20',
                            'zAddAssetAttr-Master Fingerprint-21',
                            'zGenAlbum-Creation Date-22',
                            'zGenAlbum-Start Date-23',
                            'zGenAlbum-End Date-24',
                            'ParentzGenAlbum-UUID-25',
                            'ParentzGenAlbum-Cloud GUID-26',
                            'ParentzGenAlbum- Title-27',
                            'zGenAlbum- Title-User&System Applied-28',
                            'zGenAlbum-UUID-29',
                            'zGenAlbum-Cloud GUID-30',
                            'zGenAlbum-Creator Bundle Id-31',
                            'ParentzGenAlbum-Creation Date-32',
                            'ParentzGenAlbum-Pending Items Count-33',
                            'ParentzGenAlbum-Pending Items Type-34',
                            'ParentzGenAlbum-Kind-35',
                            'ParentzGenAlbum-Cloud-Local-State-36',
                            'ParentzGenAlbum-Sync Event Order Key-37',
                            'ParentzGenAlbum-Pinned-38',
                            'ParentzGenAlbum-Custom Sort Key-39',
                            'ParentzGenAlbum-Custom Sort Ascending-40',
                            'ParentzGenAlbum-Is Prototype-41',
                            'ParentzGenAlbum-Project Document Type-42',
                            'ParentzGenAlbum-Custom Query Type-43',
                            'ParentzGenAlbum-Trashed State-44',
                            'ParentzGenAlbum-Trash Date-45',
                            'ParentzGenAlbum-Cloud Delete State-46',
                            'zGenAlbum-Pending Items Count-47',
                            'zGenAlbum-Pending Items Type-48',
                            'zGenAlbum- Cached Photos Count-49',
                            'zGenAlbum- Cached Videos Count-50',
                            'zGenAlbum- Cached Count-51',
                            'zGenAlbum-Has Unseen Content-52',
                            'zGenAlbum-Unseen Asset Count-53',
                            'zGenAlbum-zENT- Entity-54',
                            'zGenAlbum-Album Kind-55',
                            'zGenAlbum-Cloud_Local_State-56',
                            'zGenAlbum-Sync Event Order Key-57',
                            'zGenAlbum-Pinned-58',
                            'zGenAlbum-Custom Sort Key-59',
                            'zGenAlbum-Custom Sort Ascending-60',
                            'zGenAlbum-Is Prototype-61',
                            'zGenAlbum-Project Document Type-62',
                            'zGenAlbum-Custom Query Type-63',
                            'zGenAlbum-Trashed State-64',
                            'zGenAlbum-Trash Date-65',
                            'zGenAlbum-Cloud Delete State-66')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available from PhotoData-Photos.sqlite for Assets in Non-Shared Albums')

            db.close()
        return

    elif (version.parse(iosversion) >= version.parse("15")) & (version.parse(iosversion) < version.parse("16")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',       
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
            WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
        END AS 'ParentzGenAlbum-Is Prototype',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',       
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
            LEFT JOIN Z_27ASSETS z27Assets ON z27Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z27Assets.Z_27ALBUMS
            LEFT JOIN Z_26ALBUMLISTS z26AlbumLists ON z26AlbumLists.Z_26ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z26AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65], row[66], row[67], row[68], row[69]))

                counter += 1

            description = 'Parses Assets associated with Non-Shared Albums found in the PhotoData-Photos.sqlite' \
                          ' from iOS 15. Parses limited asset data with full non-shared album data.'
            report = ArtifactHtmlReport('Photos.sqlite-E-Asset_In_Albums')
            report.start_artifact_report(report_folder, 'Ph22-Assets in Non-Shared Albums-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-zPK-1',
                            'zAsset-Directory-Path-2',
                            'zAsset-Filename-3',
                            'zAddAssetAttr- Original Filename-4',
                            'zCldMast- Original Filename-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAsset-Syndication State-7',
                            'zAsset-Bundle Scope-8',
                            'zAddAssetAttr- Imported by Bundle Identifier-9',
                            'zAddAssetAttr-Imported By Display Name-10',
                            'zAsset-Visibility State-11',
                            'zAsset-Saved Asset Type-12',
                            'zAddAssetAttr-Share Type-13',
                            'zAsset- SortToken -CameraRoll-14',
                            'zAsset-Added Date-15',
                            'zCldMast-Creation Date-16',
                            'zAddAssetAttr-Time Zone Name-17',
                            'zAddAssetAttr-EXIF-String-18',
                            'zAsset-Modification Date-19',
                            'zAsset-Last Shared Date-20',
                            'zAsset-Trashed Date-21',
                            'zAddAssetAttr-zPK-22',
                            'zAsset-UUID = store.cloudphotodb-23',
                            'zAddAssetAttr-Master Fingerprint-24',
                            'zGenAlbum-Creation Date-25',
                            'zGenAlbum-Start Date-26',
                            'zGenAlbum-End Date-27',
                            'ParentzGenAlbum-UUID-28',
                            'ParentzGenAlbum-Cloud GUID-29',
                            'ParentzGenAlbum- Title-30',
                            'zGenAlbum- Title-User&System Applied-31',
                            'zGenAlbum-UUID-32',
                            'zGenAlbum-Cloud GUID-33',
                            'zGenAlbum-Imported by Bundle Identifier-34',
                            'ParentzGenAlbum-Creation Date-35',
                            'ParentzGenAlbum-Pending Items Count-36',
                            'ParentzGenAlbum-Pending Items Type-37',
                            'ParentzGenAlbum-Kind-38',
                            'ParentzGenAlbum-Cloud-Local-State-39',
                            'ParentzGenAlbum-Sync Event Order Key-40',
                            'ParentzGenAlbum-Pinned-41',
                            'ParentzGenAlbum-Custom Sort Key-42',
                            'ParentzGenAlbum-Custom Sort Ascending-43',
                            'ParentzGenAlbum-Is Prototype-44',
                            'ParentzGenAlbum-Project Document Type-45',
                            'ParentzGenAlbum-Custom Query Type-46',
                            'ParentzGenAlbum-Trashed State-47',
                            'ParentzGenAlbum-Trash Date-48',
                            'ParentzGenAlbum-Cloud Delete State-49',
                            'zGenAlbum-Pending Items Count-50',
                            'zGenAlbum-Pending Items Type-51',
                            'zGenAlbum- Cached Photos Count-52',
                            'zGenAlbum- Cached Videos Count-53',
                            'zGenAlbum- Cached Count-54',
                            'zGenAlbum-Has Unseen Content-55',
                            'zGenAlbum-Unseen Asset Count-56',
                            'zGenAlbum-zENT- Entity-57',
                            'zGenAlbum-Album Kind-58',
                            'zGenAlbum-Cloud_Local_State-59',
                            'zGenAlbum-Sync Event Order Key-60',
                            'zGenAlbum-Pinned-61',
                            'zGenAlbum-Custom Sort Key-62',
                            'zGenAlbum-Custom Sort Ascending-63',
                            'zGenAlbum-Is Prototype-64',
                            'zGenAlbum-Project Document Type-65',
                            'zGenAlbum-Custom Query Type-66',
                            'zGenAlbum-Trashed State-67',
                            'zGenAlbum-Trash Date-68',
                            'zGenAlbum-Cloud Delete State-69')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available from PhotoData-Photos.sqlite for Assets in Non-Shared Albums')

            db.close()
        return

    elif version.parse(iosversion) >= version.parse("16"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        DateTime(zGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Creation Date',
        DateTime(zGenAlbum.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Start Date',
        DateTime(zGenAlbum.ZENDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-End Date',		
        ParentzGenAlbum.ZUUID AS 'ParentzGenAlbum-UUID',
        ParentzGenAlbum.ZCLOUDGUID AS 'ParentzGenAlbum-Cloud GUID',
        ParentzGenAlbum.ZTITLE AS 'ParentzGenAlbum- Title',
        zGenAlbum.ZTITLE AS 'zGenAlbum- Title-User&System Applied',
        zGenAlbum.ZUUID AS 'zGenAlbum-UUID',        
        zGenAlbum.ZCLOUDGUID AS 'zGenAlbum-Cloud GUID',    
        zGenAlbum.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zGenAlbum-Imported by Bundle Identifier',       
        DateTime(ParentzGenAlbum.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Creation Date',
        ParentzGenAlbum.ZPENDINGITEMSCOUNT AS 'ParentzGenAlbum-Pending Items Count',
        CASE ParentzGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'ParentzGenAlbum-Pending Items Type',
        CASE ParentzGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZKIND || ''
        END AS 'ParentzGenAlbum-Kind',
        CASE ParentzGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'ParentzGenAlbum-Cloud-Local-State',		
        ParentzGenAlbum.ZSYNCEVENTORDERKEY AS 'ParentzGenAlbum-Sync Event Order Key',
        CASE ParentzGenAlbum.ZISPINNED
            WHEN 0 THEN '0-ParentzGenAlbum Not Pinned-0'
            WHEN 1 THEN '1-ParentzGenAlbum Pinned-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPINNED || ''
        END AS 'ParentzGenAlbum-Pinned',
        CASE ParentzGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'ParentzGenAlbum-Custom Sort Key',
        CASE ParentzGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'ParentzGenAlbum-Custom Sort Ascending',
        CASE ParentzGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN '0-ParentzGenAlbum Not Prototype-0'
            WHEN 1 THEN '1-ParentzGenAlbum Prototype-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZISPROTOTYPE || ''
        END AS 'ParentzGenAlbum-Is Prototype',
        CASE ParentzGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'ParentzGenAlbum-Project Document Type',
        CASE ParentzGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'ParentzGenAlbum-Custom Query Type',
        CASE ParentzGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN '0-ParentzGenAlbum Not In Trash-0'
            WHEN 1 THEN '1-ParentzGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZTRASHEDSTATE || ''
        END AS 'ParentzGenAlbum-Trashed State',
        DateTime(ParentzGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'ParentzGenAlbum-Trash Date',
        CASE ParentzGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN '0-ParentzGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN '1-ParentzGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || ParentzGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'ParentzGenAlbum-Cloud Delete State',
        zGenAlbum.ZPENDINGITEMSCOUNT AS 'zGenAlbum-Pending Items Count',        
        CASE zGenAlbum.ZPENDINGITEMSTYPE
            WHEN 1 THEN 'No-1'
            WHEN 24 THEN '24-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPENDINGITEMSTYPE || ''
        END AS 'zGenAlbum-Pending Items Type',
        zGenAlbum.ZCACHEDPHOTOSCOUNT AS 'zGenAlbum- Cached Photos Count',
        zGenAlbum.ZCACHEDVIDEOSCOUNT AS 'zGenAlbum- Cached Videos Count',       
        zGenAlbum.ZCACHEDCOUNT AS 'zGenAlbum- Cached Count',
        CASE zGenAlbum.ZHASUNSEENCONTENT
            WHEN 0 THEN 'No Unseen Content-StillTesting-0'
            WHEN 1 THEN 'Unseen Content-StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZHASUNSEENCONTENT || ''
        END AS 'zGenAlbum-Has Unseen Content',        
        zGenAlbum.ZUNSEENASSETSCOUNT AS 'zGenAlbum-Unseen Asset Count',        		
        CASE zGenAlbum.Z_ENT
            WHEN 27 THEN '27-LPL-SPL-CPL_Album-DecodingVariableBasedOniOS-27'
            WHEN 28 THEN '28-LPL-SPL-CPL-Shared_Album-DecodingVariableBasedOniOS-28'
            WHEN 29 THEN '29-Shared_Album-DecodingVariableBasedOniOS-29'
            WHEN 30 THEN '30-Duplicate_Album-Pending_Merge-30'
            WHEN 35 THEN '35-SearchIndexRebuild-1600KIND-35'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.Z_ENT || ''
        END AS 'zGenAlbum-zENT- Entity',        
        CASE zGenAlbum.ZKIND
            WHEN 2 THEN '2-Non-Shared-Album-2'
            WHEN 1505 THEN '1505-Shared-Album-1505'
            WHEN 1506 THEN '1506-Import_Session_AssetsImportedatSameTime-1506_RT'
            WHEN 1508 THEN '1508-My_Projects_Album_CalendarCardEct_RT'
            WHEN 1509 THEN '1509-SWY_Synced_Conversation_Media-1509'
            WHEN 1510 THEN '1510-Duplicate_Album-Pending_Merge-1510'
            WHEN 3571 THEN '3571-Progress-Sync-3571'
            WHEN 3572 THEN '3572-Progress-OTA-Restore-3572'
            WHEN 3573 THEN '3573-Progress-FS-Import-3573'
            WHEN 3998 THEN '3998-Project Root Folder-3998'
            WHEN 3999 THEN '3999-Parent_Root_for_Generic_Album-3999'
            WHEN 4000 THEN '4000-Parent_is_Folder_on_Local_Device-4000'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZKIND || ''
        END AS 'zGenAlbum-Album Kind',       
        CASE zGenAlbum.ZCLOUDLOCALSTATE
            WHEN 0 THEN '0-iCldPhotos_ON=Asset_In_Shared_Album-Conv_or_iCldPhotos.sqlite-OFF=Generic_Album-0'
            WHEN 1 THEN '1-iCldPhotos.sqlite-ON=Asset_In_Generic_Album-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDLOCALSTATE || ''
        END AS 'zGenAlbum-Cloud_Local_State',        
        zGenAlbum.ZSYNCEVENTORDERKEY AS 'zGenAlbum-Sync Event Order Key',       
        CASE zGenAlbum.ZISPINNED
            WHEN 0 THEN 'zGenAlbum-Local Not Pinned-0'
            WHEN 1 THEN 'zGenAlbum-Local Pinned-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPINNED || ''
        END AS 'zGenAlbum-Pinned',       
        CASE zGenAlbum.ZCUSTOMSORTKEY
            WHEN 0 THEN '0-zGenAlbum-Sorted_Manually-0_RT'
            WHEN 1 THEN '1-zGenAlbum-CusSrtAsc0=Sorted_Newest_First-CusSrtAsc1=Sorted_Oldest_First-1-RT'
            WHEN 5 THEN '5-zGenAlbum-Sorted_by_Title-5_RT'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTKEY || ''
        END AS 'zGenAlbum-Custom Sort Key',        
        CASE zGenAlbum.ZCUSTOMSORTASCENDING
            WHEN 0 THEN '0-zGenAlbum-Sorted_Newest_First-0'
            WHEN 1 THEN '1-zGenAlbum-Sorted_Oldest_First-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMSORTASCENDING || ''
        END AS 'zGenAlbum-Custom Sort Ascending',       
        CASE zGenAlbum.ZISPROTOTYPE
            WHEN 0 THEN 'zGenAlbum-Not Prototype-0'
            WHEN 1 THEN 'zGenAlbum-Prototype-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZISPROTOTYPE || ''
        END AS 'zGenAlbum-Is Prototype',       
        CASE zGenAlbum.ZPROJECTDOCUMENTTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPROJECTDOCUMENTTYPE || ''
        END AS 'zGenAlbum-Project Document Type',         
        CASE zGenAlbum.ZCUSTOMQUERYTYPE
            WHEN 0 THEN '0-StillTesting'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCUSTOMQUERYTYPE || ''
        END AS 'zGenAlbum-Custom Query Type',            
        CASE zGenAlbum.ZTRASHEDSTATE
            WHEN 0 THEN 'zGenAlbum Not In Trash-0'
            WHEN 1 THEN 'zGenAlbum Album In Trash-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZTRASHEDSTATE || ''
        END AS 'zGenAlbum-Trashed State',
        DateTime(zGenAlbum.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zGenAlbum-Trash Date',          
        CASE zGenAlbum.ZCLOUDDELETESTATE
            WHEN 0 THEN 'zGenAlbum Cloud Not Deleted-0'
            WHEN 1 THEN 'zGenAlbum Cloud Album Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZCLOUDDELETESTATE || ''
        END AS 'zGenAlbum-Cloud Delete State',        
        CASE zGenAlbum.ZSEARCHINDEXREBUILDSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Search Index State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Search Index State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Search Index State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZSEARCHINDEXREBUILDSTATE || ''
        END AS 'zGenAlbum-Search Index Rebuild State',        
        CASE zGenAlbum.ZDUPLICATETYPE
            WHEN 0 THEN '0-StillTesting GenAlbumDuplicateType-0'
            WHEN 1 THEN 'Duplicate Asset_Pending-Merge-1'
            WHEN 2 THEN '2-StillTesting GenAlbumDuplicateType-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZDUPLICATETYPE || ''
        END AS 'zGenAlbum-Duplicate Type',        
        CASE zGenAlbum.ZPRIVACYSTATE
            WHEN 0 THEN '0-StillTesting GenAlbm-Privacy State-0'
            WHEN 1 THEN '1-StillTesting GenAlbm-Privacy State-1'
            WHEN 2 THEN '2-StillTesting GenAlbm-Privacy State-2'
            ELSE 'Unknown-New-Value!: ' || zGenAlbum.ZPRIVACYSTATE || ''
        END AS 'zGenAlbum-Privacy State'
        FROM ZASSET zAsset
            LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
            LEFT JOIN Z_28ASSETS z28Assets ON z28Assets.Z_3ASSETS = zAsset.Z_PK
            LEFT JOIN ZGENERICALBUM zGenAlbum ON zGenAlbum.Z_PK = z28Assets.Z_28ALBUMS
            LEFT JOIN Z_27ALBUMLISTS z27AlbumLists ON z27AlbumLists.Z_27ALBUMS = zGenAlbum.Z_PK
            LEFT JOIN ZALBUMLIST zAlbumList ON zAlbumList.Z_PK = z27AlbumLists.Z_2ALBUMLISTS
            LEFT JOIN ZGENERICALBUM ParentzGenAlbum ON ParentzGenAlbum.Z_PK = zGenAlbum.ZPARENTFOLDER
            LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
        WHERE zGenAlbum.ZKIND = 2
        ORDER BY zAsset.ZDATECREATED
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54],
                                  row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
                                  row[64], row[65], row[66], row[67], row[68], row[69], row[70], row[71], row[72],
                                  row[73], row[74]))

                counter += 1

            description = 'Parses Assets associated with Non-Shared Albums found in the PhotoData-Photos.sqlite' \
                          ' from iOS 16-17. Parses limited asset data with full non-shared album data.'
            report = ArtifactHtmlReport('Photos.sqlite-E-Asset_In_Albums')
            report.start_artifact_report(report_folder, 'Ph22-Assets in Non-Shared Albums-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-zPK-1',
                            'zAsset-Directory-Path-2',
                            'zAsset-Filename-3',
                            'zAddAssetAttr- Original Filename-4',
                            'zCldMast- Original Filename-5',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-6',
                            'zAsset-Syndication State-7',
                            'zAsset-Bundle Scope-8',
                            'zAddAssetAttr.Imported by Bundle Identifier-9',
                            'zAddAssetAttr-Imported By Display Name-10',
                            'zAsset-Visibility State-11',
                            'zAsset-Saved Asset Type-12',
                            'zAddAssetAttr-Share Type-13',
                            'zAsset-Active Library Scope Participation State-14',
                            'zAsset- SortToken -CameraRoll-15',
                            'zAsset-Added Date-16',
                            'zCldMast-Creation Date-17',
                            'zAddAssetAttr-Time Zone Name-18',
                            'zAddAssetAttr-EXIF-String-19',
                            'zAsset-Modification Date-20',
                            'zAsset-Last Shared Date-21',
                            'zAsset-Trashed Date-22',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-23',
                            'zAddAssetAttr-zPK-24',
                            'zAsset-UUID = store.cloudphotodb-25',
                            'zAddAssetAttr-Master Fingerprint-26',
                            'zGenAlbum-Creation Date-27',
                            'zGenAlbum-Start Date-28',
                            'zGenAlbum-End Date-29',
                            'ParentzGenAlbum-UUID-30',
                            'ParentzGenAlbum-Cloud GUID-31',
                            'ParentzGenAlbum- Title-32',
                            'zGenAlbum- Title-User&System Applied-33',
                            'zGenAlbum-UUID-34',
                            'zGenAlbum-Cloud GUID-35',
                            'zGenAlbum-Imported by Bundle Identifier-36',
                            'ParentzGenAlbum-Creation Date-37',
                            'ParentzGenAlbum-Pending Items Count-38',
                            'ParentzGenAlbum-Pending Items Type-39',
                            'ParentzGenAlbum-Kind-40',
                            'ParentzGenAlbum-Cloud-Local-State-41',
                            'ParentzGenAlbum-Sync Event Order Key-42',
                            'ParentzGenAlbum-Pinned-43',
                            'ParentzGenAlbum-Custom Sort Key-44',
                            'ParentzGenAlbum-Custom Sort Ascending-45',
                            'ParentzGenAlbum-Is Prototype-46',
                            'ParentzGenAlbum-Project Document Type-47',
                            'ParentzGenAlbum-Custom Query Type-48',
                            'ParentzGenAlbum-Trashed State-49',
                            'ParentzGenAlbum-Trash Date-50',
                            'ParentzGenAlbum-Cloud Delete State-51',
                            'zGenAlbum-Pending Items Count-52',
                            'zGenAlbum-Pending Items Type-53',
                            'zGenAlbum- Cached Photos Count-54',
                            'zGenAlbum- Cached Videos Count-55',
                            'zGenAlbum- Cached Count-56',
                            'zGenAlbum-Has Unseen Content-57',
                            'zGenAlbum-Unseen Asset Count-58',
                            'zGenAlbum-zENT- Entity-59',
                            'zGenAlbum-Album Kind-60',
                            'zGenAlbum-Cloud_Local_State-61',
                            'zGenAlbum-Sync Event Order Key-62',
                            'zGenAlbum-Pinned-63',
                            'zGenAlbum-Custom Sort Key-64',
                            'zGenAlbum-Custom Sort Ascending-65',
                            'zGenAlbum-Is Prototype-66',
                            'zGenAlbum-Project Document Type-67',
                            'zGenAlbum-Custom Query Type-68',
                            'zGenAlbum-Trashed State-69',
                            'zGenAlbum-Trash Date-70',
                            'zGenAlbum-Cloud Delete State-71',
                            'zGenAlbum-Search Index Rebuild State-72',
                            'zGenAlbum-Duplicate Type-73',
                            'zGenAlbum-Privacy State-74')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph22-Assets in Non-Shared Albums-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No data available from PhotoData-Photos.sqlite for Assets in Non-Shared Albums')

        db.close()
        return


__artifacts_v2__ = {
    'Ph22-Assets in Non-Shared Albums-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite 22 Assets in Non-Shared Albums',
        'description': 'Parses Assets associated with Non-Shared Albums found in PhotoData-Photos.sqlite and'
                       ' supports iOS 11-17. Parses limited assets data with full non-shared album data.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '1.1',
        'date': '2024-04-13',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-E-Asset_In_Albums',
        'notes': '',
        'paths': '*/mobile/Media/PhotoData/Photos.sqlite*',
        'function': 'get_ph22assetsinnonsharedalbumsphdapsql'
    }
}
