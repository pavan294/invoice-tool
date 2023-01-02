
import { TradingStages } from '@trading/cdk-patterns';
import { Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { Role } from 'aws-cdk-lib/aws-iam';
import { BlockPublicAccess, Bucket, BucketEncryption } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';


export interface S3StackProperties extends StackProps {
  
  /**
   * Relates resources to ownership and intent
   * @default - None
   */
  context: string
  
  /**
   * Stage as identifier
   * @default - None
   */
  stage: TradingStages

 
}
export class S3Stack extends Stack {

  private readonly stage: TradingStages;
  private readonly context: string;

  private namePrefix() {
    return `${this.stage}-${this.context}`;
  }

  constructor(scope: Construct, id: string, props: S3StackProperties) {
    super(scope, id, props);

    this.stage = props.stage;
    this.context = props.context;
    
    const irsaApiRole = Role.fromRoleArn(
      this,
      'irsa-api-role-api',
      `arn:aws:iam::${Stack.of(this).account}:role/${this.stage}-${this.context}-nordpool-invoice-downloader-api-irsa`,
      {mutable: true},
    );

    const irsaCronJobRole = Role.fromRoleArn(
      this,
      'irsa-api-role-cron-job',
      `arn:aws:iam::${Stack.of(this).account}:role/${this.stage}-${this.context}-nordpool-invoice-downloader-cronjob-irsa`,
      {mutable: true},
    );

    // Create bucket
    const s3Bucket = new Bucket(this, 's3-bucket', {
      bucketName: `${this.stage}-devops-ewe-trading-backoffice`,
      removalPolicy: RemovalPolicy.RETAIN,
      autoDeleteObjects: false,
      versioned: true,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      encryption: BucketEncryption.S3_MANAGED,
      lifecycleRules: [
        {
          enabled: true,
          prefix: "invoices/",
          abortIncompleteMultipartUploadAfter: Duration.days(7),
          expiration: Duration.days(500),
          noncurrentVersionExpiration: Duration.days(500),
    }]})

    // Grant access to roles

    s3Bucket.grantRead(irsaApiRole)
    s3Bucket.grantWrite(irsaCronJobRole)


  }
}