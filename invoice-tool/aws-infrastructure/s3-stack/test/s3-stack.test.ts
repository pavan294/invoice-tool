
import { TradingStages } from '@trading/cdk-patterns';
import { App } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { S3Stack, S3StackProperties } from '../lib/s3-stack-stack';



test('stack created', () => {

    const app = new App();
    let props : S3StackProperties = { 
        stage: TradingStages.Dev, 
        context: "test", 
    };
    const testStack = new S3Stack(app,'s3-test-stack', props);
    const template = Template.fromStack(testStack);
})