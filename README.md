# angular-test-no-tears
Automatic module imports for Angular tests. No more tears.

Ever run your Angular tests, have about ten fail, and see something like this?

```
Failed: Template parse errors:
Can't bind to 'value' since it isn't a known property of 'mat-list-option'.
1. If 'mat-list-option' is an Angular component and it has 'value' input, then verify that it is part of this module.
2. If 'mat-list-option' is a Web Component then add 'CUSTOM_ELEMENTS_SCHEMA' to the '@NgModule.schemas' of this component to suppress this message.
3. To allow any property add 'NO_ERRORS_SCHEMA' to the '@NgModule.schemas' of this component. ("
    <mat-list-option
      *ngFor="let item of list"
      [ERROR ->][value]="item"
      [ngClass]="{ filtered: hideOption(item) }"
      color="primary"
```

Well, no more! Simply run `angular-test-no-tears.py path-to-angular-html-file` and you will get an output like the following:

```
MatCardModule,
MatIconModule,
MatDividerModule,
MatCheckboxModule,
MatListModule,
DECLARATIONS:
ShuttleSubListComponent,
```

These are the imports that you need for your Jasmine tests. That's it.

## Known issues

- it only traverses one component deep. If component A has a nested component B, and component B has a nested component C, it will only get the imports from component B. A workaround is to run it on component B to get all imports for component C, then just add the imports from component B into component A.

- does not get DI injected dependencies (e.g. in the constructor.) I'm working on this.

- the Python code is probably the worst I've ever written. It does work pretty well though.

- the paths to the repo are hard-coded. Change them in the script before running.
