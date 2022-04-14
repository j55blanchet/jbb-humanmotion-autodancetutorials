// import { DefaultAzureCredential } from '@azure/identity';
import { BlobServiceClient } from '@azure/storage-blob';

// const credential = new DefaultAzureCredential();

const blobServiceClient = new BlobServiceClient(
  'https://dartrobotlabstorage.blob.core.windows.net/study-video-uploads?sv=2020-08-04&ss=bf&srt=co&sp=wdacitfx&se=2025-04-14T21:31:43Z&st=2022-04-14T13:31:43Z&spr=https&sig=RoRBLMKyg%2FUB48b2M1MLDLc%2FIsdNhkK66KaHvL%2BI0Y0%3D',
  // 'https://dartrobotlabstorage.blob.core.windows.net/study-video-uploads?sp=acw&st=2021-04-07T02:19:35Z&se=2022-04-07T10:19:35Z&sv=2020-02-10&sr=c&sig=9fpKagbOjUqAjHF579%2FW7KiM4U8YcBrbI8J70tH35Y4%3D',
  // credential,
);

export default class AzureUploader {
  public static async upload(data: Blob, blobName: string): Promise<void> {
    const client = blobServiceClient.getContainerClient('study-video-uploads');

    const blockBlobClient = client.getBlockBlobClient(blobName);

    await blockBlobClient.uploadData(data);
  }
}
