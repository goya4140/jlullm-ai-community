# -*- coding: utf-8 -*-
import unittest,json,copy,sys,tempfile,shutil
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build
ROOT=Path(__file__).resolve().parents[1]
class PublicationTests(unittest.TestCase):
    def setUp(self):self.d=json.loads((ROOT/'content/digests/2026-10-20-embodied-ai.json').read_text())
    def test_unreviewed_cannot_publish(self):
        self.d['reviewed_by']='  '
        with self.assertRaises(ValueError):build.validate(self.d)
    def test_impossible_date_rejected(self):
        self.d['date']='2026-02-30'
        with self.assertRaises(ValueError):build.validate(self.d)
    def test_executable_link_rejected(self):
        self.d['topics'][0]['links']=[{'title':'bad','url':'javascript:alert(1)'}]
        with self.assertRaises(ValueError):build.validate(self.d)
    def test_duplicate_topic_anchor_rejected(self):
        self.d['topics'][1]['id']=self.d['topics'][0]['id']
        with self.assertRaises(ValueError):build.validate(self.d)
    def test_content_cannot_insert_markup(self):
        self.d['title']='<img src=x onerror=alert(1)>'
        self.d['topics'][0]['paragraphs']=['</p><script>alert(1)</script>']
        page=build.detail(self.d)
        self.assertNotIn('<img src=x',page)
        self.assertNotIn('<script>alert(1)</script>',page)
        self.assertIn('&lt;script&gt;',page)
    def test_embedded_json_cannot_close_script(self):
        self.assertNotIn('</script>',build.safe_json({'value':'</script><script>alert(1)</script>'}))
    def test_drafts_never_enter_output_and_removal_is_effective(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for folder in ('content','templates','web'):shutil.copytree(ROOT/folder,root/folder)
            draft=copy.deepcopy(self.d);draft['id']='2026-10-21-private-draft';draft['status']='draft';draft['title']='UNPUBLISHED_DRAFT_MARKER'
            (root/'content/digests/draft.json').write_text(json.dumps(draft))
            out=root/'docs'
            with patch.object(build,'ROOT',root),patch.object(build,'OUT',out):
                build.build()
                self.assertFalse((out/'daily'/draft['id']).exists())
                self.assertNotIn('UNPUBLISHED_DRAFT_MARKER',''.join(p.read_text() for p in out.rglob('*.html')))
                self.d['status']='draft';(root/'content/digests/2026-10-20-embodied-ai.json').write_text(json.dumps(self.d))
                build.build()
                self.assertFalse((out/'daily'/self.d['id']).exists())
    def test_unknown_publication_state_is_error(self):
        self.d['status']='publsihed'
        with self.assertRaises(ValueError):build.validate(self.d)
if __name__=='__main__':unittest.main()
