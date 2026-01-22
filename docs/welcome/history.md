# The Object Builder for i's origin story

TOBi's creators originally employed a classic IBM i development model.  At some point, however, their third-party source control product was end-of-lifed while still containing several unfixed bugs, with no available upgrade path.  This caused no small amount of development pain, and lessons were learned.  After that, it was decided to stick to in-house and open source technologies.

Different third-party change management products were evaluated, but many had a steep price and seemed to require more change management red tape than was preferred.  It was felt that using something like Jira or Trac for issue management, Git for source control, and TOBi + Make for builds would give the desired simplicity while staying powerful and flexible.

We at S4i Systems are firm believers in both open source and giving back to the community, and are pleased to release The Object Builder as an open source project.  

IBM has recognized the potential in this project and the need for high quality build tooling for the IFS.  IBM has agreed to host the TOBi project under the IBM account and has invested heavily in adding a number of features to make TOBi a robust tool for the masses that can easily integrated to a variety of IDE and terminal based development environments.