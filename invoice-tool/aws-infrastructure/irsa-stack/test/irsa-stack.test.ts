
import { TradingStages } from '@trading/cdk-patterns';
import { App } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';

import { K8sNamespace, K8sServiceAccountApi } from '../lib/enums';
import { AwsIrsaAppAssetsStack, AwsIrsaAppAssetsStackProperties } from '../lib/irsa-stack';

test('stack created', () => {

    const app = new App();
    let props : AwsIrsaAppAssetsStackProperties = { 
        stage: TradingStages.Dev, 
        context: "test", 
        k8sNamespace: K8sNamespace.Dev, 
        k8sServiceAccount: K8sServiceAccountApi.Dev,
    };
    const testStack = new AwsIrsaAppAssetsStack(app,'irsa-iam-assets-test-stack', props);
    const template = Template.fromStack(testStack);
})