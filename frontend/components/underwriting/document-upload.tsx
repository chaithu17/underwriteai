'use client';

import { useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function DocumentUpload({
  borrowerProfileId,
  onUpload
}: {
  borrowerProfileId: number | null;
  onUpload: (params: { documentType: string; file: File }) => Promise<void>;
}) {
  const [documentType, setDocumentType] = useState('W2');
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement | null>(null);

  const handleUpload = async () => {
    if (!borrowerProfileId || !fileRef.current?.files?.[0]) {
      return;
    }

    setUploading(true);
    try {
      await onUpload({ documentType, file: fileRef.current.files[0] });
      fileRef.current.value = '';
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Document Intelligence</CardTitle>
        <CardDescription>Upload W-2, pay stubs, and bank statements for OCR + AI extraction.</CardDescription>
      </CardHeader>
      <CardContent className='space-y-4'>
        <div className='grid gap-2'>
          <Label>Document Type</Label>
          <Input value={documentType} onChange={(e) => setDocumentType(e.target.value)} />
        </div>

        <div className='grid gap-2'>
          <Label>File</Label>
          <Input ref={fileRef} type='file' accept='.pdf,.png,.jpg,.jpeg,.tiff' />
        </div>

        <Button onClick={handleUpload} disabled={!borrowerProfileId || uploading}>
          {uploading ? 'Uploading...' : 'Upload + Extract'}
        </Button>
      </CardContent>
    </Card>
  );
}
